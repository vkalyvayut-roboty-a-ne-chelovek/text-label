from text_label.bus import Bus
from text_label.statechart import Statechart
from text_label.gui import Gui
from text_label.exporters.text_directory import TextDirectoryExporter


def run():
    bus = Bus()
    statechart = Statechart(name='statechart', bus=bus)
    gui = Gui(bus=bus)
    td_export = TextDirectoryExporter(bus=bus)

    statechart.run()
    gui.run()


if __name__ == '__main__':
    run()
