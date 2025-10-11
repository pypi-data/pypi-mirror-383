import pytest

from src.show_dialog.inputs import Inputs


@pytest.fixture
def inputs_instance():
    return Inputs(title='Foo', description='Bar')
