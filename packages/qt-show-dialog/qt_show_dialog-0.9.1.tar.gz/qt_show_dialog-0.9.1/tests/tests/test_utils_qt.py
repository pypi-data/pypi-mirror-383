import pytest

from src.show_dialog.config import ASSETS_DIR
from src.show_dialog.ui.forms import resources_rc  # noqa: F401  # Initialize Qt resources
from src.show_dialog.utils_qt import list_resources, read_file
from tests.libs.config import TEST_ASSETS_DIR


class TestListResources:
    def test_resource_path(self):
        files = list_resources(':/stylesheets')
        assert files == [':/stylesheets/style_01.css', ':/stylesheets/style_02.css']

    def test_absolute_path(self):
        base_path = TEST_ASSETS_DIR / 'stylesheets'
        files = list_resources(base_path)
        assert files == [f'{base_path}/style_01.css']

    def test_dir_does_not_exist_resource(self):
        with pytest.raises(NotADirectoryError):
            list_resources('foo')

    def test_dir_does_not_exist_absolute(self):
        with pytest.raises(NotADirectoryError):
            list_resources(TEST_ASSETS_DIR / 'foo')


class TestReadFile:
    def test_read_file(self):
        file_content = read_file(':/stylesheets/style_01.css')
        assert 'No style applied' in file_content

    def test_absolute_path(self):
        file_content = read_file(ASSETS_DIR / 'stylesheets/style_01.css')
        assert 'No style applied' in file_content

    def test_file_does_not_exist(self):
        with pytest.raises(FileNotFoundError):
            read_file('foo')
