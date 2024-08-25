from text_label.bus import Bus
from text_label.statechart import Statechart
from text_label.gui import Gui


def run():
    bus = Bus()
    statechart = Statechart(name='statechart', bus=bus)
    gui = Gui(bus=bus)

    statechart.run()
    gui.run()

    print(statechart.spy())


if __name__ == '__main__':
    run()
