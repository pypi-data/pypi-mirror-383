import json

import pytest
import yaml
from pytest_params import params

from src.show_dialog import DataFileType, Inputs
from tests.libs.fixtures import inputs_instance  # noqa: F401


class TestDataFileType:
    @params(
        'file, expected',
        [
            ('json lowercase', 'foo.json', DataFileType.JSON),
            ('json uppercase', 'foo.JSON', DataFileType.JSON),
            ('yaml lowercase', 'foo.yaml', DataFileType.YAML),
            ('yml mixed case', 'foo.yMl', DataFileType.YAML),
        ],
    )
    def test_from_file(self, file, expected):
        assert DataFileType.from_file(file) is expected


class TestInputs:
    def test_instantiation(self):
        inputs = Inputs(dialog_title='Baz', title='Foo', description='Bar')

        assert inputs.dialog_title == 'Baz'
        assert inputs.title == 'Foo'
        assert inputs.description == 'Bar'

    def test_instantiation_defaults(self):
        inputs = Inputs()

        assert inputs.dialog_title == ''
        assert inputs.title == ''
        assert inputs.description == ''
        assert inputs.description_md is False
        assert inputs.timeout == 0
        assert inputs.timeout_pass is False
        assert inputs.timeout_text == '%v'
        assert inputs.pass_button_text == ''
        assert inputs.fail_button_text == ''
        assert inputs.pass_button_icon == ''
        assert inputs.fail_button_icon == ''

    @params(
        'file_name, file_type',
        [
            ('json', 'test.json', DataFileType.JSON),
            ('yaml', 'test.yaml', DataFileType.YAML),
            ('json auto', 'test.json', DataFileType.AUTO),
            ('yaml auto', 'test.yaml', DataFileType.AUTO),
            ('yml auto', 'test.yml', DataFileType.AUTO),
        ],
    )
    def test_to_file(self, tmp_path, inputs_instance, file_name, file_type):
        file = tmp_path / file_name
        inputs_instance.to_file(file, file_type)

        with open(file) as f:
            open_func = (
                json.load if DataFileType.from_file(file) is DataFileType.JSON else yaml.safe_load
            )
            data = open_func(f)

        inputs_instance_2 = Inputs.from_dict(data)
        assert inputs_instance == inputs_instance_2

    def test_to_file_invalid(self, tmp_path, inputs_instance):
        file = tmp_path / 'foo.bar'
        with pytest.raises(ValueError):
            inputs_instance.to_file(file)

    @params(
        'file_name',
        [
            ('json', 'test.json'),
            ('yaml', 'test.yaml'),
            ('yml', 'test.yml'),
        ],
    )
    def test_from_file(self, tmp_path, inputs_instance, file_name):
        file = tmp_path / file_name
        inputs_instance.to_file(file)

        inputs_instance_2 = Inputs.from_file(file)
        assert inputs_instance == inputs_instance_2

    def test_from_file_invalid(self, tmp_path, inputs_instance):
        file = tmp_path / 'foo.bar'
        with pytest.raises(ValueError):
            Inputs.from_file(file)

    def test_create(self):
        base = Inputs(title='Foo', description='Bar')
        new = base.create(Inputs(description='Baz', dialog_title='qux'))

        assert isinstance(new, Inputs)
        assert new == Inputs(title='Foo', description='Baz', dialog_title='qux')

    @params('base_value', [('True', True), ('False', False)])
    def test_create_with_boolean(self, base_value):
        """
        Boolean fields are not taken into consideration when creating new instances
        and maintain the base value.
        """
        base = Inputs(description_md=base_value)
        new_inputs = Inputs()
        assert new_inputs.description_md is False
        new = base.create(new_inputs)

        assert new.description_md is base_value
