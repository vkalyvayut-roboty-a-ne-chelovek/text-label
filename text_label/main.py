from collections import namedtuple
import json
import pathlib

from miros import ActiveObject
from miros import return_status, signals, Event
from miros import spy_on

from typing import Optional

class Bus:
    def __init__(self):
        self.objects = {}

    def register(self, name, obj):
        self.objects[name] = obj

    def __getitem__(self, item):
        return self.objects.get(item, None)

    def __getattr__(self, item):
        return self.objects.get(item, None)


class Gui:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.bus.register('gui', self)

    def run(self):
        pass


class Project:
    def __init__(self, categories: Optional[list] = (), data: Optional[list] = ()):
        self.categories: list = list(categories)
        self.data: list = list(data)

    @staticmethod
    def load_project_from_path(path_to_project: pathlib.Path):
        with open(path_to_project, mode='r', encoding='utf-8') as project_handle:
            raw = json.loads(project_handle.read())
            return Project(categories=raw['categories'], data=raw['data'])

    def add_category(self, category: str):
        if category not in self.categories:
            self.categories.append(category)

    def add_text(self, text: str):
        self.data.append([text, None])


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

    def on_load_project_in_init(self, path_to_project: pathlib.Path):
        self.project = Project.load_project_from_path(path_to_project)

    def on_add_category_in_in_project(self, category: str):
        self.project.add_category(category)

    def on_import_text_from_input_in_in_project(self, text: str):
        self.project.add_text(text)

    def on_import_text_from_file_in_in_project(self, path_to_file: pathlib.Path):
        with open(path_to_file, mode='r', encoding='utf-8') as text_handle:
            self.project.add_text(text_handle.read())

    def launch_new_project_event(self):
        self.post_fifo(Event(signal=signals.NEW_PROJECT))

    def launch_load_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=path_to_project))

    def launch_add_category_event(self, category: str):
        self.post_fifo(Event(signal=signals.ADD_CATEGORY, payload=category))

    def launch_import_text_from_input(self, text: str):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_INPUT, payload=text))

    def launch_import_text_from_file(self, path_to_file: pathlib.Path):
        self.post_fifo(Event(signal=signals.IMPORT_TEXT_FROM_FILE, payload=path_to_file))


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
    elif e.signal == signals.IMPORT_TEXT_FROM_INPUT:
        status = return_status.HANDLED
        s.on_import_text_from_input_in_in_project(e.payload)
    elif e.signal == signals.IMPORT_TEXT_FROM_FILE:
        status = return_status.HANDLED
        s.on_import_text_from_file_in_in_project(e.payload)
    else:
        status = return_status.SUPER
        s.temp.fun = init

    return status


def run():
    bus = Bus()
    statechart = Statechart(name='statechart', bus=bus)
    gui = Gui(bus=bus)

    statechart.run()
    gui.run()


if __name__ == '__main__':
    run()
