import unittest

from text_label.history import History


class TestHistory(unittest.TestCase):
    def test_initial_state(self):
        h = History(initial_state=1)
        assert h.states == [1]
        assert h.get_current_state() == 1

    def test_add_state(self):
        h = History(initial_state=1)
        h.add_state(2)
        assert h.get_current_state() == 2
        assert h.states == [1, 2]

    def test_rollback_state(self):
        h = History(initial_state=1)
        h.add_state(2)
        assert h.get_current_state() == 2
        assert h.rollback_state() == 2
        assert h.get_current_state() == 1
        assert h.states == [1]

        assert h.rollback_state() == 1
        assert h.get_current_state() == 1
        assert h.states == [1]


if __name__ == '__main__':
    unittest.main()
