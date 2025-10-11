from enum import IntEnum


class ExitCode(IntEnum):
    """
    App exit code.
    ``0`` represents success, otherwise failure.
    """

    Pass = 0
    """
    One of:

    * ``Pass`` button was clicked.
    * Timeout occurred but ``timeout_pass`` is ``True`` in inputs.
    * ``Ctrl+P`` shortcut was used.
    """
    Unknown = 1
    """
    An unknown error occurred, likely from an uncaught exception.
    """
    Fail = 2
    """
    ``Fail`` button was clicked.
    """
    Cancel = 3
    """
    One of:

    * Dialog was closed with the ``X`` button.
    * ``Ctrl+Q`` shortcut was used.
    """
    Timeout = 4
    """
    Timeout occurred and ``timeout_pass`` is ``False`` in inputs.
    """
