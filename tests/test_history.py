import unittest

from text_label.main import History


class TestHistory(unittest.TestCase):
    def test_initial_state(self):
        h = History(initial_state=[1])
        assert h.states == [[1]]

    def test_apply_changes(self):
        h = History(initial_state=[1])
        h.apply_changes([2])
        assert h.states == [[1], [2]]

    def test_prev_state(self):
        h = History(initial_state=[1])
        h.apply_changes([2])
        assert h.prev_state() == [2]
        assert h.states == [[1]]


if __name__ == '__main__':
    unittest.main()
