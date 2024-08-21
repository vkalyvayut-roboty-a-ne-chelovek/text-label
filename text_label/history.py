import copy
from typing import List


class History:
    def __init__(self, initial_state):
        self.states: List = [initial_state]

    def add_state(self, new_state):
        self.states.append(copy.deepcopy(new_state))

    def rollback_state(self):
        if len(self.states) > 1:
            return self.states.pop()
        else:
            return copy.deepcopy(self.states[0])

    def get_current_state(self):
        return copy.deepcopy(self.states[-1])