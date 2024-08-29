import copy
import hashlib
import json
import pathlib
from typing import Optional, Union, Tuple

from text_label.text_info import TextInfo
from text_label.history import History


class Project:
    def __init__(self, categories: Optional[dict[int, str]] = None, data: Optional[list] = ()):
        self.categories: dict[int, str] = self._make_categories_from_raw(categories if categories else {})
        self.data: list[TextInfo] = self._make_data_from_raw(data)
        self.history = History(self._get_snapshot())

    @staticmethod
    def _make_categories_from_raw(categories: dict[Union[str, int]]) -> dict[int, str]:
        return {int(k): str(v) for k, v in categories.items()}

    @staticmethod
    def _make_data_from_raw(data: list) -> list[TextInfo]:
        return [TextInfo(text=text_info[0], category_id=text_info[1]) if len(text_info) == 2 else TextInfo(text=text_info[0])
                for text_info in list(data)]

    def _get_snapshot(self) -> Tuple:
        return copy.deepcopy((self.categories, self.data))

    @staticmethod
    def load_project_from_path(path_to_project: pathlib.Path):
        with open(path_to_project, mode='r', encoding='utf-8') as project_handle:
            raw = json.loads(project_handle.read())
            return Project(categories=raw['categories'], data=raw['data'])

    def save_project(self, path_to_project: pathlib.Path):
        with open(path_to_project, mode='w', encoding='utf-8') as project_handle:
            raw = {"version": 0, "categories": self.categories, "data": [[text_info.text, text_info.category_id] for text_info in self.data]}
            project_handle.write(json.dumps(raw))
        self.history = History(self._get_snapshot())

    def add_category(self, category: str):
        if category not in self.categories.values():
            next_id = list(self.categories.keys())[-1]+1 if len(self.categories) > 0 else 0
            self.categories[next_id] = category
            self.history.add_state(self._get_snapshot())

    def remove_category(self, category_id: int):
        self.categories.pop(category_id)
        for text_id, text_info in enumerate(self.data):
            if text_info.category_id == category_id:
                self.data[text_id].category_id = None
                self.history.add_state(self._get_snapshot())

    def add_text(self, text: str):
        self.data.append(TextInfo(text=text))
        self.history.add_state(self._get_snapshot())

    def remove_text(self, text_id: int):
        self.data.pop(text_id)
        self.history.add_state(self._get_snapshot())

    def mark_text(self, text_id: int, category_id: int):
        self.data[text_id].category_id = category_id
        self.history.add_state(self._get_snapshot())

    def get_texts(self, category_id: Optional[int] = None) -> list[TextInfo]:
        data = self.data
        if category_id is not None:
            data = [text for text in data if text.category_id == category_id]
        return data

    def undo(self):
        self.history.rollback_state()
        self.categories, self.data = self.history.get_current_state()

    def get_name(self):
        return str(hashlib.md5(str(self.history).encode('utf-8')).hexdigest())
