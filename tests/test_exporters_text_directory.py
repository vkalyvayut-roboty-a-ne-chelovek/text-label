import glob
import os.path
import pathlib
import tempfile
import unittest

from text_label.project import Project
from text_label.exporters.text_directory import TextDirectoryExporter


class TestExportersTextDirectory(unittest.TestCase):
    def test_export(self):
        path_to_project = pathlib.Path('./assets/test.json.tl')
        path_to_dir = pathlib.Path(tempfile.mktemp(prefix='test_exporters_text_directory'))

        project = Project.load_project_from_path(path_to_project)
        exporter = TextDirectoryExporter()

        exporter.export(path_to_dir, project=project)

        assert os.path.exists(pathlib.Path(path_to_dir, 'cat1'))
        assert os.path.isdir(pathlib.Path(path_to_dir, 'cat1'))

        assert os.path.exists(pathlib.Path(path_to_dir, 'cat2'))
        assert os.path.isdir(pathlib.Path(path_to_dir, 'cat2'))

        assert len(glob.glob(str(path_to_dir.resolve().absolute()) + '/*/*.txt')) == 2




if __name__ == '__main__':
    unittest.main()
