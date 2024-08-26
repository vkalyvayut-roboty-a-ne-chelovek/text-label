import pathlib

from miros import ActiveObject
from miros import return_status, signals, Event
from miros import spy_on

from text_label.project import Project


class Statechart(ActiveObject):
    def __init__(self, name: str, bus):
        super().__init__(name)
        self.bus = bus
        self.bus.register('statechart', self)
        self.project: Project = None

    def run(self):
        self.start_at(init)

    def on_new_project_in_init(self):
        self.project = Project()

        self.bus.gui.enable_menus()
        self.bus.gui.init_bindings()

        self.bus.gui.update_categories(self.project.categories)
        self.bus.gui.update_texts(self.project.get_texts())

    def on_load_project_in_init(self, path_to_project: pathlib.Path):
        self.project = Project.load_project_from_path(path_to_project)

        self.bus.gui.enable_menus()
        self.bus.gui.init_bindings()

        self.bus.gui.update_categories(self.project.categories)
        self.bus.gui.update_texts(self.project.get_texts())

    def on_add_category_in_in_project(self, category: str):
        self.project.add_category(category)

        self.bus.gui.update_categories(self.project.categories)

    def on_remove_category_in_in_project(self, category_id: int):
        self.project.remove_category(category_id)

        self.bus.gui.update_categories(self.project.categories)

    def on_import_text_from_input_in_in_project(self, text: str):
        self.project.add_text(text)

        self.bus.gui.update_texts(self.project.get_texts())

    def on_import_text_from_file_in_in_project(self, path_to_file: pathlib.Path):
        with open(path_to_file, mode='r', encoding='utf-8') as text_handle:
            self.project.add_text(text_handle.read())

            self.bus.gui.update_texts(self.project.get_texts())

    def on_mark_text_in_in_project(self, text_id: int, category_id: int):
        self.project.mark_text(text_id=text_id, category_id=category_id)

    def on_remove_text_in_in_project(self, text_id: int):
        self.project.remove_text(text_id=text_id)

        self.bus.gui.update_texts(self.project.get_texts())

    def on_save_project_in_in_project(self, path_to_project: pathlib.Path):
        self.project.save_project(path_to_project)

    def launch_new_project_event(self):
        self.post_fifo(Event(signal=signals.NEW_PROJECT))

    def launch_load_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=path_to_project))

    def launch_add_category_event(self, category: str):
        self.post_fifo(Event(signal=signals.ADD_CATEGORY, payload=category))

    def launch_remove_category_event(self, category_id: int):
        self.post_fifo(Event(signal=signals.REMOVE_CATEGORY, payload=category_id))

    def launch_import_text_from_input(self, text: str):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_INPUT, payload=text))

    def launch_import_text_from_file_event(self, path_to_file: pathlib.Path):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_FILE, payload=path_to_file))

    def launch_remove_text_event(self, text_id: int):
        self.post_fifo(Event(signal=signals.REMOVE_TEXT, payload=text_id))

    def launch_mark_text_event(self, text_id: int, category_id):
        self.post_fifo(Event(signal=signals.MARK_TEXT, payload=(text_id, category_id)))

    def launch_save_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.SAVE_PROJECT, payload=path_to_project))

    def launch_undo_event(self):
        self.post_fifo(Event(signal=signals.UNDO))

    def on_undo_project_in_in_project(self):
        self.project.undo()


@spy_on
def init(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.NEW_PROJECT:
        status = s.trans(in_project)
        s.on_new_project_in_init()
    elif e.signal == signals.LOAD_PROJECT:
        status = s.trans(in_project)
        s.on_load_project_in_init(e.payload)
    else:
        status = return_status.SUPER
        s.temp.fun = s.top

    return status


@spy_on
def in_project(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.ADD_CATEGORY:
        status = return_status.HANDLED
        s.on_add_category_in_in_project(e.payload)
    elif e.signal == signals.REMOVE_CATEGORY:
        status = return_status.HANDLED
        s.on_remove_category_in_in_project(e.payload)
    elif e.signal == signals.IMPORT_TEXT_FROM_INPUT:
        status = return_status.HANDLED
        s.on_import_text_from_input_in_in_project(e.payload)
    elif e.signal == signals.IMPORT_TEXT_FROM_FILE:
        status = return_status.HANDLED
        s.on_import_text_from_file_in_in_project(e.payload)
    elif e.signal == signals.MARK_TEXT:
        status = return_status.HANDLED
        s.on_mark_text_in_in_project(text_id=e.payload[0], category_id=e.payload[1])
    elif e.signal == signals.REMOVE_TEXT:
        status = return_status.HANDLED
        s.on_remove_text_in_in_project(text_id=e.payload)
    elif e.signal == signals.SAVE_PROJECT:
        status = return_status.HANDLED
        s.on_save_project_in_in_project(e.payload)
    elif e.signal == signals.UNDO:
        status = return_status.HANDLED
        s.on_undo_project_in_in_project()
    else:
        status = return_status.SUPER
        s.temp.fun = init

    return status
