import os.path
import pathlib
import time
import unittest
import tempfile

from miros import stripped

from text_label.text_info import TextInfo
from text_label.statechart import Statechart
from text_label.gui import TestableGui
from text_label.bus import Bus


class TestStatechart(unittest.TestCase):
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
        self.gui = TestableGui(bus=self.bus)

        self.statechart.run()
        self.gui.run()

        self.path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        self.path_to_file = pathlib.Path(os.path.dirname(__file__), 'assets', 'text.txt')

    def test_new_project_event(self):
        self.statechart.launch_new_project_event()
        self.statechart.launch_add_category_event('cat1')
        self.statechart.launch_new_project_event()
        time.sleep(0.1)

        expected_trace = '''
        [2024-08-10 14:59:20.316061] [statechart] e->start_at() top->init
        [2024-08-10 14:59:20.316658] [statechart] e->NEW_PROJECT() init->in_project
        [2024-08-10 14:59:20.316804] [statechart] e->NEW_PROJECT() in_project->in_project
        '''
        actual_trace = self.statechart.trace()

        self._assert_trace_check(expected_trace, actual_trace)

        assert self.statechart.project.categories == {}
        assert self.statechart.project.get_texts() == []

    def test_load_project_event(self):
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        time.sleep(0.1)

        expected_trace = '''
        [2024-08-09 10:14:18.371508] [statechart] e->start_at() top->init
        [2024-08-09 10:14:18.371949] [statechart] e->LOAD_PROJECT() init->in_project
        '''
        actual_trace = self.statechart.trace()

        self._assert_trace_check(expected_trace, actual_trace)

        assert self.statechart.project.categories == {0: 'cat1', 1: 'cat2'}
        assert self.statechart.project.get_texts() == [TextInfo('text1', category_id=0), TextInfo('text2'), TextInfo('text3', 1)]

    def test_add_category_event(self):
        self.statechart.launch_new_project_event()
        time.sleep(0.1)
        self.statechart.launch_add_category_event('cat1')
        self.statechart.launch_add_category_event('cat2')
        self.statechart.launch_add_category_event('cat1')
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)', 'ADD_CATEGORY:in_project', 'ADD_CATEGORY:in_project:HOOK', '<- Queued:(2) Deferred:(0)', 'ADD_CATEGORY:in_project', 'ADD_CATEGORY:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'ADD_CATEGORY:in_project', 'ADD_CATEGORY:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

        assert self.statechart.project.categories == {0: 'cat1', 1: 'cat2'}

    def test_import_text_from_input_event(self):
        self.statechart.launch_new_project_event()
        self.statechart.launch_import_text_from_input('text1')
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(1) Deferred:(0)', 'IMPORT_TEXT_FROM_INPUT:in_project', 'IMPORT_TEXT_FROM_INPUT:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

        assert self.statechart.project.get_texts() == [TextInfo('text1')]

    def test_import_text_from_file_event(self):
        self.statechart.launch_new_project_event()
        self.statechart.launch_import_text_from_file_event(self.path_to_file)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(1) Deferred:(0)', 'IMPORT_TEXT_FROM_FILE:in_project', 'IMPORT_TEXT_FROM_FILE:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

        assert self.statechart.project.get_texts() == [TextInfo('text2', None)]

    def test_mark_text_event(self):
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        self.statechart.launch_mark_text_event(text_id=1, category_id=1)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'LOAD_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(1) Deferred:(0)', 'MARK_TEXT:in_project', 'MARK_TEXT:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

        assert self.statechart.project.categories == {0: 'cat1', 1: 'cat2'}
        assert self.statechart.project.get_texts() == [TextInfo('text1', category_id=0), TextInfo('text2', category_id=1), TextInfo('text3', category_id=1)]

    def test_save_project_event(self):
        path_to_temp_project_file = pathlib.Path(tempfile.mktemp())

        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        self.statechart.launch_mark_text_event(text_id=1, category_id=1)
        self.statechart.launch_save_project_event(path_to_temp_project_file)
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        self.statechart.launch_load_project_event(path_to_project=path_to_temp_project_file)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'LOAD_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(4) Deferred:(0)', 'MARK_TEXT:in_project', 'MARK_TEXT:in_project:HOOK', '<- Queued:(3) Deferred:(0)', 'SAVE_PROJECT:in_project', 'SAVE_PROJECT:in_project:HOOK', '<- Queued:(2) Deferred:(0)', 'LOAD_PROJECT:in_project', 'LOAD_PROJECT:init', 'EXIT_SIGNAL:in_project', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(1) Deferred:(0)', 'LOAD_PROJECT:in_project', 'LOAD_PROJECT:init', 'EXIT_SIGNAL:in_project', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()
        self._assert_spy_check(expected_spy, actual_spy)

        expected_trace = '''
        [2024-08-12 12:32:40.795100] [statechart] e->start_at() top->init
        [2024-08-12 12:32:40.796069] [statechart] e->LOAD_PROJECT() init->in_project
        [2024-08-12 12:32:40.796391] [statechart] e->LOAD_PROJECT() in_project->in_project
        [2024-08-12 12:32:40.796504] [statechart] e->LOAD_PROJECT() in_project->in_project
        '''
        actual_trace = self.statechart.trace()
        self._assert_trace_check(expected_trace, actual_trace)

        assert os.path.exists(path_to_temp_project_file)

        assert self.statechart.project.categories == {0: 'cat1', 1: 'cat2'}
        assert self.statechart.project.get_texts() == [TextInfo('text1', category_id=0), TextInfo('text2', category_id=1), TextInfo('text3', category_id=1)]

    def test_undo_event(self):
        self.statechart.launch_new_project_event()
        self.statechart.launch_add_category_event('0')
        self.statechart.launch_import_text_from_input('0')
        self.statechart.launch_import_text_from_input('1')
        time.sleep(0.1)

        assert self.statechart.project.categories == {0: '0'}
        assert self.statechart.project.get_texts() == [TextInfo('0'), TextInfo('1')]

        self.statechart.launch_mark_text_event(text_id=0, category_id=0)
        time.sleep(0.1)
        assert self.statechart.project.get_texts() == [TextInfo(text='0', category_id=0), TextInfo(text='1')]

        # отменяю маркировку текста
        self.statechart.launch_undo_event()
        time.sleep(0.1)

        assert self.statechart.project.categories == {0: '0'}
        assert self.statechart.project.get_texts() == [TextInfo('0'), TextInfo('1')]

        # отменяю добавление текст '1'
        self.statechart.launch_undo_event()
        time.sleep(0.1)

        assert self.statechart.project.categories == {0: '0'}
        assert self.statechart.project.get_texts() == [TextInfo('0')]

        # отменяю добавление текст '0'
        self.statechart.launch_undo_event()
        time.sleep(0.1)

        assert self.statechart.project.categories == {0: '0'}
        assert self.statechart.project.get_texts() == []

        # отменяю добавление категории '0'
        self.statechart.launch_undo_event()
        time.sleep(0.1)

        assert self.statechart.project.categories == {}
        assert self.statechart.project.get_texts() == []

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'NEW_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(3) Deferred:(0)', 'ADD_CATEGORY:in_project', 'ADD_CATEGORY:in_project:HOOK', '<- Queued:(2) Deferred:(0)', 'IMPORT_TEXT_FROM_INPUT:in_project', 'IMPORT_TEXT_FROM_INPUT:in_project:HOOK', '<- Queued:(1) Deferred:(0)', 'IMPORT_TEXT_FROM_INPUT:in_project', 'IMPORT_TEXT_FROM_INPUT:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'MARK_TEXT:in_project', 'MARK_TEXT:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'UNDO:in_project', 'UNDO:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'UNDO:in_project', 'UNDO:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'UNDO:in_project', 'UNDO:in_project:HOOK', '<- Queued:(0) Deferred:(0)', 'UNDO:in_project', 'UNDO:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

    def test_remove_text(self):
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        time.sleep(0.1)
        self.statechart.launch_remove_text_event(0)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'LOAD_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)', 'REMOVE_TEXT:in_project', 'REMOVE_TEXT:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)

    def test_remove_category(self):
        self.statechart.launch_load_project_event(path_to_project=self.path_to_project)
        time.sleep(0.1)
        self.statechart.launch_remove_category_event(1)
        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init', 'ENTRY_SIGNAL:init', 'INIT_SIGNAL:init', '<- Queued:(0) Deferred:(0)', 'LOAD_PROJECT:init', 'SEARCH_FOR_SUPER_SIGNAL:in_project', 'ENTRY_SIGNAL:in_project', 'INIT_SIGNAL:in_project', '<- Queued:(0) Deferred:(0)', 'REMOVE_CATEGORY:in_project', 'REMOVE_CATEGORY:in_project:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self._assert_spy_check(expected_spy, actual_spy)


if __name__ == '__main__':
    unittest.main()
