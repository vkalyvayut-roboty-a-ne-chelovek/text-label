import copy
import tempfile
import unittest
import pathlib
import os.path

from text_label.project import Project
from text_label.text_info import TextInfo


class TestProject(unittest.TestCase):
    def test_new_project(self):
        project = Project()
        assert project.categories == {}
        assert project.data == []

    def test_load_project(self):
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        project = Project.load_project_from_path(path_to_project)

        assert len(project.categories) == 2
        assert len(project.data) == 3
        assert project.data[0].text == 'text1'
        assert project.data[2].category_id == 1

        assert project.data == [TextInfo(text="text1", category_id=0),
                                TextInfo("text2"),
                                TextInfo(text="text3", category_id=1)]

    def test_add_category(self):
        project = Project()
        assert project.categories == {}
        project.add_category('cat1')
        assert project.categories == {0: 'cat1'}

        project.add_category('cat1')
        assert project.categories == {0: 'cat1'}

        project.add_category('cat2')
        assert project.categories == {0: 'cat1', 1: 'cat2'}

    def test_remove_category(self):
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        project = Project.load_project_from_path(path_to_project)

        prev_categories = copy.copy(project.categories)
        project.remove_category(1)
        curr_categories = project.categories
        assert prev_categories != curr_categories

        assert project.data == [TextInfo(text="text1", category_id=0), TextInfo("text2"), TextInfo("text3")]

    def test_add_text(self):
        project = Project()
        assert project.data == []
        project.add_text('text1')

        assert project.data == [TextInfo(text='text1')]

    def test_remove_text(self):
        project = Project()
        assert project.data == []
        project.add_text('text1')
        project.add_text('text2')
        project.remove_text(0)

        assert project.data == [TextInfo('text2')]

    def test_mark_text(self):
        project = Project()
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        project = Project.load_project_from_path(path_to_project)

        project.mark_text(1, 1)
        assert project.data == [TextInfo('text1', category_id=0), TextInfo('text2', category_id=1), TextInfo('text3', category_id=1)]

    def test_get_texts(self):
        project = Project()
        project.add_text('text1')
        project.add_text('text2')
        project.add_text('text3')

        assert project.get_texts() == [TextInfo('text1'), TextInfo('text2'), TextInfo('text3')]

    def test_get_texts_of_category(self):
        project = Project()
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        project = Project.load_project_from_path(path_to_project)

        assert len(project.get_texts()) == 3
        assert len(project.get_texts(0)) == 1

    def test_save_project(self):
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.json.tl')
        project = Project.load_project_from_path(path_to_project)
        project.add_text('text4')
        project.add_text('text5')

        expected_data = [TextInfo('text1', category_id=0),
                                TextInfo('text2'),
                                TextInfo('text3', category_id=1),
                                TextInfo('text4'),
                                TextInfo('text5')]

        assert project.data == expected_data

        path_to_temp_project_file = tempfile.mktemp()
        project.save_project(path_to_temp_project_file)

        assert os.path.exists(path_to_temp_project_file)

        project = Project.load_project_from_path(path_to_project)
        project.add_text('text5')

        project = Project.load_project_from_path(path_to_temp_project_file)

        assert project.data == expected_data


if __name__ == '__main__':
    unittest.main()
