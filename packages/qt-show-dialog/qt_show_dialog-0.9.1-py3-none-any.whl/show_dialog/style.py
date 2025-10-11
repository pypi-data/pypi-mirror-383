from enum import Enum


class Style(str, Enum):  # StrEnum is Python 3.11+
    """
    Predefined styles, included in the resources file.

    To add a new style:

    1. Create the ``.css`` file under ``assets/stylesheets``.
    2. Add to ``assets/resources.qrc``, under the ``stylesheets`` folder.
       This file is XML, it's self-explanatory how to add a new entry.
    3. Rebuild the resource file to include the new CSS file with the command ``inv ui.rc``.
    4. Add a new entry to this enum, where the value is the path in the resource file,
       starting with ``:/``.
    """

    Style01 = ':/stylesheets/style_01.css'
    """No style."""
    Style02 = ':/stylesheets/style_02.css'
    """Default style."""
