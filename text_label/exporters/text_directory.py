import os.path
import pathlib
from typing import Optional, List
from tkinter import filedialog

from text_label.bus import Bus
from text_label.project import Project
from text_label.text_info import TextInfo


class TextDirectoryExporter:
    def __init__(self, bus: Optional[Bus] = None):
        self.bus = bus
        if self.bus:
            self.bus.register('exporters[text_directory]', self)

    def show_options(self):
        path_to_root_dir = filedialog.askdirectory(initialdir=pathlib.Path(__file__).parent)
        if path_to_root_dir:
            project = self.bus.statechart.project
            path_to_dir = pathlib.Path(path_to_root_dir, project.get_name())
            self.export(path_to_dir=path_to_dir, project=project)

    def export(self, path_to_dir: pathlib.Path, project: Project):
        if self.make_root_dir(path_to_dir):
            for cat_id in project.categories:
                cat_name = project.categories[cat_id]
                path_to_category_dir = self.make_category_dir(path_to_dir, category_name=cat_name)
                if path_to_category_dir:
                    self.put_text_files_in_category_dir(path_to_category_dir, texts=project.get_texts(category_id=cat_id))

    @staticmethod
    def make_root_dir(path_to_root_dir: pathlib.Path) -> bool:
        path_to_root_dir.mkdir(parents=True)
        return os.path.exists(path_to_root_dir)

    @staticmethod
    def make_category_dir(path_to_root_dir: pathlib.Path, category_name: str) -> pathlib.Path:
        path_to_category_dir = path_to_root_dir / category_name
        path_to_category_dir.mkdir(parents=True)
        return path_to_category_dir

    @staticmethod
    def put_text_files_in_category_dir(path_to_category_dir: pathlib.Path, texts: List[TextInfo]):
        for idx, text_info in enumerate(texts):
            path_to_file = path_to_category_dir / f'{idx}.txt'
            with open(path_to_file, mode='w', encoding='utf-8') as file_handle:
                file_handle.write(text_info.text)

