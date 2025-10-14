import os
import gazu
import re
from fnmatch import fnmatch

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.flow_entities.entities import Entity, Property

from ..utils.kabaret.flow_entities.entities import EntityView
from ..utils.flow.file_processing import ProcessSequenceFiles

from .departments import Department
from .maputils import ItemMap, CreateItemAction, ClearMapAction, SimpleCreateAction
from .lib import AssetDependency, DropAssetAction  # , KitsuSettingsView
from .kitsu import KitsuSequence, KitsuShot, UpdateItemsKitsuSettings
from .site import SiteJobsPoolNames
from .dependency import get_dependencies
from .file import GenericRunAction
from .users import ToggleBookmarkAction
from .shot import SequenceCollection


class Casting(flow.Map):

    ICON = ("icons.flow", "casting")

    drag_assets = flow.Child(DropAssetAction)

    @classmethod
    def mapped_type(cls):
        return AssetDependency

    def columns(self):
        return ["Name", "Description"]

    def row(self, item):
        _, row = super(Casting, self).row(item)

        return item.get().oid(), row

    def _fill_row_cells(self, row, item):
        asset = item.get()
        row["Name"] = asset.id.get()
        row["Description"] = asset.description.get()


class DisplayKitsuSettings(flow.Action):

    _map = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context and context.endswith(".inline")

    def run(self, button):
        displayed = self._map._display_kitsu_settings.get()
        self._map._display_kitsu_settings.set(not displayed)
        self._map.touch()


class ShotDepartments(flow.Object):

    layout = flow.Child(Department).ui(expanded=True)
    animation = flow.Child(Department).ui(expanded=True)
    compositing = flow.Child(Department).ui(expanded=True)


class PlayblastChoiceValue(flow.values.ChoiceValue):
    
    CHOICES = ['Layout', 'Blocking', 'Animation', 'Compositing']

    def __init__(self, parent, name):
        super(PlayblastChoiceValue, self).__init__(parent, name)
        self._to_update = True
        self._exclude_choice = None

    def choices(self):
        choices = self.CHOICES.copy()

        if self._exclude_choice is not None:
            choices.remove(self._exclude_choice)
        
        return choices
    
    def exclude_choice(self, choice):
        self._exclude_choice = choice
        self.touch()
    
    def update(self, exclude_choice=None):
        self._exclude_choice = exclude_choice
        self._to_update = False

        if self.get() == exclude_choice:
            self.set(self.choices()[0])
            self._to_update = True
        
        self.touch()
    
    def notify(self):
        if self._watched and self._to_update:
            self._mng.parent.child_value_changed(self)


class ComparePreviews(GenericRunAction):

    ICON = ('icons.libreflow', 'compare-previews')

    _shot = flow.Parent()

    task_1 = flow.Param('Animation', PlayblastChoiceValue).watched()
    task_2 = flow.Param('Compositing', PlayblastChoiceValue).watched()

    FILE_BY_TASK = {
        'Layout': '/tasks/layout/files/layout_movie_mov',
        'Blocking': '/tasks/animation/files/blocking_movie_mov',
        'Animation': '/tasks/animation/files/animation_movie_mov',
        'Compositing': '/tasks/compositing/files/compositing_movie_mov'
    }

    def runner_name_and_tags(self):
        return 'RV', []
    
    def get_run_label(self):
        return 'Compare previews'

    def get_buttons(self):
        self.message.set('<h2>Compare previews</h2>')
        self.task_1.revert_to_default()
        self.task_2.revert_to_default()

        return ['Compare', 'Close']
    
    def get_version(self, button):
        return super(GenericRunAction, self).get_version(button)
    
    def needs_dialog(self):
        return True
    
    def extra_argv(self):
        return ['-wipe', '-autoRetime', '0'] + self._previews
    
    def child_value_changed(self, child_value):
        if child_value is self.task_1:
            self.task_2.update(exclude_choice=self.task_1.get())
            self.task_1.exclude_choice(self.task_2.get())
        elif child_value is self.task_2:
            self.task_1.update(exclude_choice=self.task_2.get())
            self.task_2.exclude_choice(self.task_1.get())
    
    def _get_preview_path(self, preview_oid):
        path = None

        if self.root().session().cmds.Flow.exists(preview_oid):
            preview = self.root().get_object(preview_oid)
            head = preview.get_head_revision()

            if head is not None and head.get_sync_status() == 'Available':
                path = head.get_path()
        
        return path
    
    def run(self, button):
        if button == 'Close':
            return
        
        preview_1_oid = self._shot.oid() + self.FILE_BY_TASK[self.task_1.get()]
        preview_2_oid = self._shot.oid() + self.FILE_BY_TASK[self.task_2.get()]

        preview_1_path = self._get_preview_path(preview_1_oid)

        if preview_1_path is None:
            self.message.set((
                '<h2>Compare previews</h2>'
                f'<font color=#D5000D>{self.task_1.get()} preview not available !'
            ))
            return self.get_result(close=False)
        
        preview_2_path = self._get_preview_path(preview_2_oid)

        if preview_2_path is None:
            self.message.set((
                '<h2>Compare previews</h2>'
                f'<font color=#D5000D>{self.task_2.get()} preview not available !'
            ))
            return self.get_result(close=False)
        
        self._previews = [preview_1_path, preview_2_path]
        result = super(ComparePreviews, self).run(button)

        return self.get_result(close=False)


class Shot(KitsuShot):

    ICON = ("icons.flow", "shot")

    _sequence = flow.Parent(2)
    settings = flow.Child(ContextualView).ui(hidden=True)
    # casting = flow.Child(Casting)

    description = flow.Param("")
    tasks = flow.Child(ShotDepartments).ui(expanded=True)
    
    compare = flow.Child(ComparePreviews)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(shot=self.name())


class Shots(ItemMap):

    ICON = ("icons.flow", "shot")

    item_prefix = "p"

    _display_kitsu_settings = flow.BoolParam(False)

    with flow.group("Kitsu"):
        toggle_kitsu_settings = flow.Child(DisplayKitsuSettings)
        update_kitsu_settings = flow.Child(UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Shot)

    def columns(self):
        names = ["Name"]

        if self._display_kitsu_settings.get():
            names.extend(
                ["Movement", "Nb frames", "Frame in", "Frame out", "Multiplan"]
            )

        return names

    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()

        if self._display_kitsu_settings.get():
            row["Nb frames"] = item.kitsu_settings["nb_frames"].get()

            data = item.kitsu_settings["data"].get()

            row["Movement"] = data["movement"]
            row["Frame in"] = data["frame_in"]
            row["Frame out"] = data["frame_out"]
            row["Multiplan"] = data["multiplan"]


class PlayblastItem(flow.Object):

    to_submit = flow.SessionParam(False).ui(editor='bool').watched()
    use_simplify = flow.SessionParam(False).ui(editor='bool')
    reduce_textures = flow.SessionParam(False).ui(editor='bool')
    target_texture_width = flow.SessionParam(False).ui(editor='bool')
    priority = flow.SessionParam(10).ui(editor='int').watched()

    def child_value_changed(self, child_value):
        # Do nothing by default
        pass


class PlayblastFileRevision(flow.values.ChoiceValue):

    STRICT_CHOICES = False

    _file_pb = flow.Parent()

    def set_default_value(self, value):
        if value == 'last':
            revision_names = self._file_pb.revision_names()
            if revision_names:
                value = revision_names[-1]
            else:
                value = ''
        
        super(PlayblastFileRevision, self).set_default_value(value)

    def choices(self):
        return self._file_pb.revision_names() or []


class PlayblastFile(PlayblastItem):
    
    _task_pb = flow.Parent(2)
    _shot_pb = flow.Parent(4)
    _sequence = flow.Parent(7)

    revision = flow.Param('last', PlayblastFileRevision).watched()
    
    file_oid = flow.Computed(cached=True)
    display_name = flow.Computed(cached=True)
    department = flow.Computed(cached=True)
    exists = flow.Computed(cached=True)
    revision_available = flow.Computed(cached=True)

    def revision_names(self):
        if not self.exists.get():
            return None
        
        file_object = self.root().get_object(self.file_oid.get())
        return file_object.get_revision_names(published_only=True)

    def _compute_file_oid(self):
        return '%s/shots/%s/tasks/%s/files/%s' % (
            self._sequence.oid(),
            self._shot_pb.name(),
            self.department.get(),
            self.name()
        )
    
    def _compute_exists(self):
        return self.root().session().cmds.Flow.exists(self.file_oid.get())
    
    def _compute_department(self):
        file_data = self._task_pb.file_data(self.name())
        return file_data['department']
    
    def _compute_display_name(self):
        file_data = self._task_pb.file_data(self.name())
        return file_data['display_name']
    
    def _compute_revision_available(self):
        if not self.exists.get() or not self.revision.get():
            return False
        
        file_object = self.root().get_object(self.file_oid.get())
        rev_object = file_object.get_revision(self.revision.get())

        return rev_object.get_sync_status() == 'Available'

    def compute_child_value(self, child_value):
        if child_value is self.file_oid:
            self.file_oid.set(self._compute_file_oid())
        elif child_value is self.exists:
            self.exists.set(self._compute_exists())
        elif child_value is self.display_name:
            self.display_name.set(self._compute_display_name())
        elif child_value is self.department:
            self.department.set(self._compute_department())
        elif child_value is self.revision_available:
            self.revision_available.set(self._compute_revision_available())
    
    def child_value_changed(self, child_value):
        if child_value is self.revision:
            self.revision_available.touch()
    
    def submit(self, pool_name):
        if not self.to_submit.get() or not self.exists.get() or not self.revision_available.get():
            return
        
        file_object = self.root().get_object(self.file_oid.get())

        file_object.submit_blender_playblast_job.revision_name.set(self.revision.get())
        file_object.submit_blender_playblast_job.use_simplify.set(self.use_simplify.get())
        file_object.submit_blender_playblast_job.reduce_textures.set(self.reduce_textures.get())
        file_object.submit_blender_playblast_job.target_texture_width.set(self.target_texture_width.get())
        file_object.submit_blender_playblast_job.priority.set(self.priority.get())
        file_object.submit_blender_playblast_job.pool.set(pool_name)
        file_object.submit_blender_playblast_job.run('Add to render pool')


class PlayblastFiles(flow.DynamicMap):
    
    _task_pb = flow.Parent()
    
    @classmethod
    def mapped_type(cls):
        return PlayblastFile
    
    def mapped_names(self, page_num=0, page_size=None):
        return self._task_pb.file_names()


class PlayblastTask(PlayblastItem):
    
    _shot_pb = flow.Parent(2)
    files = flow.Child(PlayblastFiles)

    def file_names(self):
        task_data = self._shot_pb.task_data(self.name())
        return task_data['files_data'].keys()

    def file_data(self, file_name):
        task_data = self._shot_pb.task_data(self.name())
        return task_data['files_data'][file_name]
    
    def child_value_changed(self, child_value):
        if child_value is self.to_submit:
            for file in self.files.mapped_items():
                file.to_submit.set(self.to_submit.get())
        elif child_value is self.priority:
            for file in self.files.mapped_items():
                file.priority.set(self.priority.get())
    
    def submit(self, pool_name):
        for file in self.files.mapped_items():
            file.submit(pool_name)


class PlayblastTasks(flow.DynamicMap):
    
    _shot_pb = flow.Parent()
    
    @classmethod
    def mapped_type(cls):
        return PlayblastTask
    
    def mapped_names(self, page_num=0, page_size=None):
        return self._shot_pb.task_names()


class PlayblastShot(PlayblastItem):
    
    _render_action = flow.Parent(2)
    tasks = flow.Child(PlayblastTasks)

    def task_names(self):
        return self._render_action.shot_task_names()
    
    def task_data(self, task_name):
        return self._render_action.shot_task_data(task_name)
    
    def child_value_changed(self, child_value):
        if child_value is self.to_submit:
            for task in self.tasks.mapped_items():
                task.to_submit.set(self.to_submit.get())
        elif child_value is self.priority:
            for task in self.tasks.mapped_items():
                task.priority.set(self.priority.get())
    
    def submit(self, pool_name):
        for task in self.tasks.mapped_items():
            task.submit(pool_name)


class PlayblastShots(flow.DynamicMap):
    
    sequence = flow.Parent(2)
    
    @classmethod
    def mapped_type(cls):
        return PlayblastShot
    
    def mapped_names(self, page_num=0, page_size=None):
        return self.sequence.shots.mapped_names()


class RenderSequencePlayblasts_XX(flow.Action):
    
    shots = flow.Child(PlayblastShots).ui(
        expanded=True,
        # action_submenus=True,
        items_action_submenus=True,
    )
    submit_all = flow.SessionParam(False).ui(editor='bool').watched()
    default_priority = flow.SessionParam(10).ui(editor='int').watched()
    pool = flow.Param('default', SiteJobsPoolNames)
    
    def __init__(self, parent, name):
        super(RenderSequencePlayblasts, self).__init__(parent, name)
        self._task_names = None
        self._tasks_data = None
    
    def _get_tasks_infos(self):
        template = self.root().project().admin.dependency_templates['shot']
        deps = template.get_dependencies()
        default_dep_names = template.get_default_dependency_names()
        
        task_names = []
        tasks_data = {}
        for name in default_dep_names:
            dep = deps[name]
            files_data = {}
            
            for file_name, file_data in dep['files'].items():
                if fnmatch(file_name, '*.blend'):
                    # Keep only Blender files
                    mapped_name = file_name.replace('.', '_')
                    files_data[mapped_name] = dict(
                        display_name=file_name,
                        department=file_data['department']
                    )
            
            if files_data:
                task_names.append(name)
                tasks_data[name] = dict(files_data=files_data)
        
        return task_names, tasks_data
    
    def _ensure_tasks_infos(self):
        if self._task_names is None or self._tasks_data is None:
            self._task_names, self._tasks_data = self._get_tasks_infos()
        
        return self._task_names, self._tasks_data
    
    def shot_task_names(self):
        return self._ensure_tasks_infos()[0]
    
    def shot_task_data(self, task_name):
        return self._ensure_tasks_infos()[1][task_name]
    
    def set_to_submit(self, to_submit):
        for shot in self.shots.mapped_items():
            shot.to_submit.set(to_submit)
    
    def set_default_priority(self, priority):
        for shot in self.shots.mapped_items():
            shot.priority.set(priority)
    
    def child_value_changed(self, child_value):
        if child_value is self.submit_all:
            self.set_to_submit(self.submit_all.get())
        elif child_value is self.default_priority:
            self.set_default_priority(self.default_priority.get())
    
    def get_buttons(self):
        return ['Submit playblasts', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for shot in self.shots.mapped_items():
            shot.submit(self.pool.get())


class RenderSequencePlayblasts(ProcessSequenceFiles):
    
    ICON = ('icons.gui', 'film-strip-with-two-photograms')
    
    def get_job_pool_names(self):
        site = self.root().project().get_current_site()
        return ['default'] + site.pool_names.get()
    
    def submit_blender_playblast_job(self, shot_name, dept_name, file_name, revision_name, use_simplify, reduce_textures, target_texture_width, priority=10, pool_name='default'):
        file_name = file_name.replace('.', '_')
        oid = f'{self._sequence.oid()}/shots/{shot_name}/tasks/{dept_name}/files/{file_name}'
        file = self.root().get_object(oid)
        
        file.submit_blender_playblast_job.revision_name.set(revision_name)
        file.submit_blender_playblast_job.use_simplify.set(use_simplify)
        file.submit_blender_playblast_job.reduce_textures.set(reduce_textures)
        file.submit_blender_playblast_job.target_texture_width.set(target_texture_width)
        file.submit_blender_playblast_job.priority.set(priority)
        file.submit_blender_playblast_job.pool.set(pool_name)
        file.submit_blender_playblast_job.run('Submit job')
    
    def submit_afterfx_playblast_job(self, shot_name, dept_name, file_name, revision_name, priority=10, pool_name='default'):
        file_name = file_name.replace('.', '_')
        oid = f'{self._sequence.oid()}/shots/{shot_name}/tasks/{dept_name}/files/{file_name}'
        file = self.root().get_object(oid)
        
        file.submit_ae_playblast.revision.set(revision_name)
        # file.submit_ae_playblast.priority.set(priority)
        file.submit_ae_playblast.pool.set(pool_name)
        file.submit_ae_playblast.run('Submit')
    
    def _compute_files_data(self):
        # Keep only tasks which contain Blender files
        blender_files_by_task = self.get_shot_task_files(['*.blend', '*.aep'], ['playblast'])
        
        shots = self._sequence.shots
        files_data = []
        
        for shot in shots.mapped_items():
            tasks_files = []
            
            for task_name, task_files in blender_files_by_task:
                files = []
                
                for file_name, file_data in task_files:
                    file_mapped_name = file_name.replace('.', '_')
                    dept_name = file_data['department']
                    file_oid = f'{shot.oid()}/tasks/{dept_name}/files/{file_mapped_name}'
                    
                    if not self.root().session().cmds.Flow.exists(file_oid):
                        # Skip if file does not exist in the flow
                        continue
                    
                    file = self.root().get_object(file_oid)
                    revision_statuses = file.get_revision_statuses(published_only=True)
                    head = file.get_head_revision(sync_status='Available')
                    
                    default_revision = head.name() if head is not None else None
                    
                    if not revision_statuses:
                        self.root().session().log_warning(
                            f'File {file.oid()} has no published revision available'
                        )
                        continue
                    
                    files.append(dict(
                        oid=file.oid(),
                        name=file_name,
                        shot=shot.name(),
                        department=dept_name,
                        revisions=revision_statuses,
                        default_revision=default_revision
                    ))
                
                tasks_files.append(dict(
                    name=task_name,
                    files=files
                ))
            
            files_data.append(dict(
                oid=shot.oid(),
                name=shot.name(),
                tasks=tasks_files
            ))
        
        return files_data
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.utils.ui.file_processing.RenderSequencePlayblastsWidget'


class UploadSequencePlayblastsToKitsu(ProcessSequenceFiles):
    
    ICON = ('icons.libreflow', 'kitsu-upload')

    def allow_context(self, context):
        return (
            context
            and self.root().project().kitsu_config().configured.get()
        )
    
    def get_task_statutes(self):
        return self.root().project().kitsu_api().get_task_statutes()
    
    def get_kitsu_task_type(self, task_name):
        dependencies = self.root().project().admin.dependency_templates['shot'].get_dependencies()
        kitsu_data = dependencies[task_name].get('kitsu', None)
        
        if kitsu_data is None:
            return None
        
        return kitsu_data.get('task_type', 'UNDEFINED')
    
    def upload_playblast_to_kitsu(self, file_oid, revision_name, task_type, target_task_status, comment):
        file = self.root().get_object(file_oid)
        file.upload_playblast.revision_name.set(revision_name)
        file.upload_playblast.target_task_type.set(task_type)
        file.upload_playblast.target_task_status.set(target_task_status)
        file.upload_playblast.comment.set(comment)
        
        file.upload_playblast.run(None)
    
    def _compute_files_data(self):
        # Search for playblast files
        playblasts_files_by_task = self.get_shot_task_files(['*.mov'])
        # print(blender_files_by_task)
        
        shots = self._sequence.shots
        files_data = []
        
        for shot in shots.mapped_items():
            tasks_files = []
            
            for task_name, task_files in playblasts_files_by_task:
                files = []
                default_kitsu_task_type = self.get_kitsu_task_type(task_name)
                
                for file_name, file_data in task_files:
                    file_mapped_name = file_name.replace('.', '_')
                    dept_name = file_data['department']
                    file_oid = f'{shot.oid()}/tasks/{dept_name}/files/{file_mapped_name}'
                    
                    if not self.root().session().cmds.Flow.exists(file_oid):
                        # Skip if file does not exist in the flow
                        continue
                    
                    file = self.root().get_object(file_oid)
                    revision_statuses = file.get_revision_statuses(published_only=True)
                    head = file.get_head_revision(sync_status='Available')
                    
                    default_revision = head.name() if head is not None else None
                    
                    if not revision_statuses:
                        self.root().session().log_warning(
                            f'File {file.oid()} has no published revision available'
                        )
                        continue
                    
                    task_types = file.upload_playblast.target_task_type.choices()
                    
                    if default_kitsu_task_type is not None:
                        file.upload_playblast.target_task_type.set(default_kitsu_task_type)
                        
                        if len(task_types) == 1:
                            # Site has no Kitsu priviledge, and single task type depends on file name
                            # => Change to Kitsu task type specified by dependency
                            task_types = [default_kitsu_task_type]
                    else:
                        file.upload_playblast.target_task_type.revert_to_default()
                    
                    files.append(dict(
                        oid=file.oid(),
                        name=file_name,
                        shot=shot.name(),
                        department=dept_name,
                        revisions=revision_statuses,
                        default_revision=default_revision,
                        task_types=task_types,
                        default_task_type=file.upload_playblast.target_task_type.get(),
                        current_task_status=file.upload_playblast.current_task_status.get(),
                        default_task_status=file.upload_playblast.target_task_status.get()
                    ))
                
                tasks_files.append(dict(
                    name=task_name,
                    files=files
                ))
            
            files_data.append(dict(
                oid=shot.oid(),
                name=shot.name(),
                tasks=tasks_files
            ))
        
        return files_data
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.utils.ui.file_processing.UploadSequencePlayblastsWidget'


class Sequence(KitsuSequence):

    ICON = ("icons.flow", "sequence")

    _map = flow.Parent()

    settings = flow.Child(ContextualView).ui(hidden=True)
    description = flow.Param("")
    toggle_bookmark = flow.Child(ToggleBookmarkAction)
    shots = flow.Child(Shots).ui(expanded=True,
                                 default_height=600)
    
    render_playblasts = flow.Child(RenderSequencePlayblasts)
    upload_playblasts = flow.Child(UploadSequencePlayblastsToKitsu)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(sequence=self.name())


class ClearSequencesAction(ClearMapAction):
    def run(self, button):
        for sequence in self._map.mapped_items():
            for shot in sequence.shots.mapped_items():
                shot.kitsu_settings.clear()

            sequence.shots.clear()
            sequence.kitsu_settings.clear()

        super(ClearSequencesAction, self).run(button)


class Sequences_XX(ItemMap):

    ICON = ("icons.flow", "sequence")

    item_prefix = "s"

    create_sequence = flow.Child(CreateItemAction)
    update_kitsu_settings = flow.Child(UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Sequence

    def columns(self):
        return ["Name"]

    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="PROD")


class Film(Entity):
    """
    Defines a film containing a list of sequences.

    Instances provide the `film` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'film')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    sequences = flow.Child(SequenceCollection).ui(
        expanded=True,
        show_filter=True,
        default_height=600
    )

    settings = flow.Child(ContextualView).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        return split[3]
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                film=self.name(),
                film_code=self.code.get(),
                film_display_name=self.display_name.get()
            )


class FilmCollection(EntityView):
    """
    Defines a collection of films.
    """

    ICON = ('icons.flow', 'film')

    add_film = flow.Child(SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Film)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_film_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()
