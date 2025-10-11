import json
from enum import Enum
from pathlib import Path
from typing import Any, Type, TypeVar

import yaml
from mashumaro import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin

T = TypeVar('T', bound='JSONFileMixin')


class DataFileType(Enum):
    AUTO = 'AUTO'
    """Use file type based on file extension."""
    JSON = 'JSON'
    YAML = 'YAML'

    @classmethod
    def from_file(cls, file: str | Path) -> 'DataFileType':
        file_path = Path(file)
        if file_path.suffix.lower() == '.json':
            file_type = DataFileType.JSON
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            file_type = DataFileType.YAML
        else:
            raise ValueError(f'Unsupported file type: {file}')

        return file_type


class JSONFileMixin(DataClassJSONMixin):
    """
    Adds the ability to load from file and save to file.
    Files can be JSON or YAML.
    """

    def to_file(
        self,
        file: str | Path,
        file_type: DataFileType = DataFileType.AUTO,
        **from_dict_kwargs: Any,
    ):
        file_path = Path(file)
        if file_type is DataFileType.AUTO:
            file_type = DataFileType.from_file(file_path)
        data = self.to_dict(**from_dict_kwargs)

        with open(file_path, 'w') as f:
            if file_type is DataFileType.JSON:
                json.dump(data, f, indent=2)
            else:
                yaml.safe_dump(data, f, default_flow_style=False, indent=2)

    @classmethod
    def from_file(
        cls: Type[T],
        file: str | Path,
        file_type: DataFileType = DataFileType.AUTO,
        **from_dict_kwargs: Any,
    ) -> T:
        file_path = Path(file)
        if file_type is DataFileType.AUTO:
            file_type = DataFileType.from_file(file_path)

        with open(file_path) as f:
            if file_type is DataFileType.JSON:
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        return cls.from_dict(data, **from_dict_kwargs)


class DefaultsMixin(DataClassDictMixin):
    """
    Add factory-like functionality.
    """

    def create(self, new_instance: DataClassDictMixin):
        """
        Create a new instance with this instance's values as defaults.

        Note that boolean fields are never updated, ie, will have the same value
        as the original/base instance, not the ``new_instance`` value.
        """
        defaults = self.to_dict()
        new_values = {
            k: v for k, v in new_instance.to_dict().items() if v and not isinstance(v, bool)
        }

        return self.__class__.from_dict(defaults | new_values)
