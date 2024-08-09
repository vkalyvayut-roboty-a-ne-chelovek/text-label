import os.path
import pathlib
import time
import unittest
from text_label.main import *
from miros import stripped


class MyTestCase(unittest.TestCase):
    @staticmethod
    def _assert_trace_check(expected_trace, actual_trace):
        with (stripped(expected_trace) as _expected_trace, stripped(actual_trace) as _actual_trace):
            assert len(_expected_trace) == len(_actual_trace), \
                f'Not enough events: expected ({len(_expected_trace)}) != actual({len(_actual_trace)})'

            for expected, actual in zip(_expected_trace, _actual_trace):
                assert expected == actual, f'{expected} != {actual}'

    @staticmethod
    def _assert_spy_check(expected_spy, actual_spy):
        assert len(expected_spy) == len(
            actual_spy), f'Not enough events: expected ({len(expected_spy)}) != actual({len(actual_spy)})'
        for expected, actual in zip(actual_spy, expected_spy):
            assert expected == actual, f'{expected} != {actual}'

    def setUp(self):
        self.bus = Bus()
        self.statechart = Statechart(name='statechart', bus=self.bus)
        self.gui = Gui(bus=self.bus)

        self.statechart.run()
        self.gui.run()

        self.path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.text-label-project')

    def test_new_project(self):
        self.statechart.launch_new_project_event()
        time.sleep(0.1)

        expected_trace = '''
        [2024-08-09 10:14:18.371508] [statechart] e->start_at() top->init
        [2024-08-09 10:14:18.371949] [statechart] e->NEW_PROJECT() init->in_project
        '''
        actual_trace = self.statechart.trace()

        self._assert_trace_check(expected_trace, actual_trace)

    def test_load_project(self):
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        time.sleep(0.1)

        expected_trace = '''
        [2024-08-09 10:14:18.371508] [statechart] e->start_at() top->init
        [2024-08-09 10:14:18.371949] [statechart] e->LOAD_PROJECT() init->in_project
        '''
        actual_trace = self.statechart.trace()

        self._assert_trace_check(expected_trace, actual_trace)


if __name__ == '__main__':
    unittest.main()
