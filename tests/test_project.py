import unittest
import pathlib
import os.path

from text_label.main import Project


class TestProject(unittest.TestCase):
    def test_new_project(self):
        project = Project()
        assert project.categories == []
        assert project.data == []

    def test_load_project(self):
        path_to_project = pathlib.Path(os.path.dirname(__file__), 'assets', 'test.text-label-project')
        project = Project.load_project_from_path(path_to_project)
        assert len(project.categories) == 2
        assert len(project.data) == 3
        assert project.data[0][0] == 'text1'
        assert project.data[2][1] == 1

    def test_add_category(self):
        project = Project()
        assert project.categories == []
        project.add_category('cat1')
        assert project.categories == ['cat1']

        project.add_category('cat1')
        assert project.categories == ['cat1']

        project.add_category('cat2')
        assert project.categories == ['cat1', 'cat2']

    def test_add_text(self):
        project = Project()
        assert project.data == []
        project.add_text('text1')

        assert project.data == [['text1', None]]

    def test_mark_text(self):
        project = Project()
        project.add_category('cat1')
        project.add_text('text1')
        project.mark_text(0, 0)

        assert project.data == [['text1', 0]]

if __name__ == '__main__':
    unittest.main()
