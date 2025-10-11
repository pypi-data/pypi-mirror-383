from dataclasses import dataclass
from enum import Enum

from .data_class import DefaultsMixin, JSONFileMixin


class Buttons(str, Enum):
    """Buttons displayed in the dialog."""

    OK = 'Ok'
    """
    Show only an OK button.

    * If ``pass_button_text`` is not specified, the text will be ``'Ok'``.
    * If ``pass_button_icon`` is not specified, no icon will be shown.
    """
    PASS_FAIL = 'Pass/Fail'
    """
    Pass/Fail buttons.

    Text can be modified with the input options ``pass_button_text`` and ``fail_button_text``.
    """
    OK_CANCEL = 'Ok/Cancel'
    """
    Ok/Cancel buttons.

    Text can be modified with the input options ``pass_button_text`` and ``fail_button_text``.
    """
    YES_NO = 'Yes/No'
    """
    Yes/No buttons.

    Text can be modified with the input options ``pass_button_text`` and ``fail_button_text``.
    """


class Theme(str, Enum):
    Light = 'Light'
    """A light theme is applied."""
    Dark = 'Dark'
    """A dark theme is applied."""
    System = 'System'
    """No theme is applied and uses the system theme."""


@dataclass(frozen=True)
class Inputs(JSONFileMixin, DefaultsMixin):
    """
    Inputs to the app.
    """

    dialog_title: str = ''
    """Title of the window."""

    title: str = ''

    description: str = ''
    """
    Text to display in the description section.

    Can be plain text or HTML. For markdown, set ``description_md`` to ``True``.
    """

    description_md: bool = False
    """
    Whether the text in the ``description`` field is markdown.

    Text in ``description`` can be plain text or HTML.
    """

    description_md_nl2br: bool = False
    """
    If ``description_md`` is ``True``, each new line is a line break, ie,
    convert newlines to ``<br>`` tags.

    If this option is not set, you can still add a new line by using the ``<br>`` tag or
    leaving two spaces at the end of a line.
    """

    timeout: int = 0
    """
    Timeout in seconds for the dialog to be automatically dismissed.

    ``0`` for no timeout.
    """

    timeout_pass: bool = False
    """
    Result at the end of timeout: Pass (``True``) or fail (``False``).
    """

    timeout_text: str = '%v'
    """
    Text format for timeout.

    * ``%p`` is replaced by the percentage completed.
    * ``%v`` is replaced by the current value.
    * ``%m`` is replaced by the total number of steps.

    Blank string to not show text.

    Examples:

    * ``'%p%'`` to show percentage completed, ex '15%'
    * ``'%vs'`` to show the number of seconds elapsed, ex '15s'
    """

    buttons: Buttons = Buttons.PASS_FAIL
    """
    Set the buttons displayed.

    See the ``Buttons`` class for available options.
    """

    pass_button_text: str = ''

    pass_button_icon: str = ''
    """
    Set the icon for the _Pass_ button.

    Can be a resource path, relative path or absolute path. See examples under ``assets/inputs``.
    """

    fail_button_text: str = ''

    fail_button_icon: str = ''
    """
    Set the icon for the _Fail_ button.

    Can be a resource path, relative path or absolute path. See examples under ``assets/inputs``.
    """

    theme: Theme = Theme.Light
    """
    Theme to be applied.

    This theme is a style and can be overridden with styling options.

    See the ``Theme`` class for available options.
    """
