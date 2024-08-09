import pathlib

from miros import ActiveObject
from miros import return_status, signals, Event
from miros import spy_on


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


class Statechart(ActiveObject):
    def __init__(self, name: str, bus):
        super().__init__(name)
        self.bus = bus
        self.bus.register('statechart', self)

    def run(self):
        self.start_at(init)

    def launch_new_project_event(self):
        self.post_fifo(Event(signal=signals.NEW_PROJECT))

    def launch_load_project_event(self, path_to_project: pathlib.Path):
        self.post_fifo(Event(signal=signals.LOAD_PROJECT, payload=path_to_project))


@spy_on
def init(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.NEW_PROJECT:
        status = s.trans(in_project)
    elif e.signal == signals.LOAD_PROJECT:
        status = s.trans(in_project)
    else:
        status = return_status.SUPER
        s.temp.fun = s.top

    return status


@spy_on
def in_project(s: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.INIT_SIGNAL:
        status = return_status.HANDLED
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
