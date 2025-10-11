import logging
import pprint
import sys
import types
from typing import Literal

from PySide6.QtWidgets import QApplication

from . import config
from .exit_code import ExitCode
from .inputs import Inputs
from .ipc.ipc_params import IpcParams
from .ui.show_dialog import ShowDialog
from .utils_qt import list_resources, read_file


def show_dialog(
    inputs: Inputs,
    *,
    stylesheet: str = config.DEFAULT_STYLE,
    ipc_params: IpcParams | None = None,
    mode: Literal['exit', 'raise', 'return'] = 'exit',
) -> ExitCode:
    """
    Create an instance of ``ShowDialog`` and show it.

    :param inputs: Inputs to the dialog.
    :param stylesheet: Stylesheet to be used. This is the whole stylesheet as a string, not a path
        to a stylesheet file.
    :param ipc_params: Inter-Process Communication parameters.
    :param mode: One of:
        * ``exit``: Exit with ``sys.exit(code)``.
        * ``raise``: Raise a ``ValueError`` exception if there was an error.
        * ``return``: Return an ``ExitCode``, regardless of whether there was an error.
    """

    app: QApplication = QApplication.instance()  # type: ignore
    if not app:
        app = QApplication()
    window = ShowDialog(app, inputs, stylesheet=stylesheet, ipc_params=ipc_params)
    window.show()
    app_response = app.exec()
    app.closeAllWindows()
    exit_code = ExitCode(app_response)

    if exit_code is not ExitCode.Pass:
        msg = f'Error: {exit_code} - {exit_code.name}'
        if mode == 'raise':
            raise ValueError(msg)
        logging.error(msg)

    if mode == 'exit':
        sys.exit(exit_code)

    return exit_code


def _parse_args():
    """
    Parse CLI arguments.
    """
    from argparse import ArgumentParser, RawTextHelpFormatter

    from . import __version__

    description = f'Show Dialog {__version__}'

    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '--inputs',
        type=str,
        help='Input parameters in the form of a JSON string that maps to the `Inputs` class.\n'
        'If both `--inputs` and `--inputs-file` are specified, `--inputs` takes precedence.',
    )
    parser.add_argument(
        '--inputs-file',
        type=str,
        help='Path to JSON or YAML file that maps to the `Inputs` class.\n'
        'If both `--inputs` and `--inputs-file` are specified, `--inputs` takes precedence.',
    )
    parser.add_argument(
        '--stylesheet',
        type=str,
        default=config.DEFAULT_STYLE,
        help=f'Path to CSS file to apply. Can be a path to an external file or one of the included '
        f'{", ".join("`"+file+"`" for file in list_resources(":/stylesheets"))}',
    )
    parser.add_argument(
        '--ipc',
        type=str,
        help='Inter-Process Communication parameters in the form of a JSON string that maps to the '
        '`IpcParams` class.\nIf specified, this process will start listening to the host:port '
        'specified for messages and respond to them. This can come from a different process.',
    )
    parser.add_argument(
        '--ipc-file',
        type=str,
        help='Path to JSON file that maps to the `IpcParams` class.\n'
        'If both `--ipc` and `--ipc-file` are specified, `--ipc` takes precedence.',
    )
    parser.add_argument(
        '--log-level',
        # Can use `logging.getLevelNamesMapping()` instead of `_nameToLevel` on python 3.11+
        choices=[level.lower() for level in logging._nameToLevel],  # noqa
        default='info',
        help='Log level to use.',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )

    return parser.parse_args()


def _set_config_values(args) -> tuple[Inputs, str | None, IpcParams | None]:
    """
    Set ``config`` values.
    """
    from . import __version__

    logging.basicConfig(level=logging.getLevelName(args.log_level.upper()))
    logging.debug(
        f'Show Dialog.\n  App version: {__version__}\n  Log level: {args.log_level}\n  '
        f'File: {sys.executable}'
    )

    # Config contents
    config_dict = {
        key: getattr(config, key, '__UNDEFINED__')
        for key in sorted(dir(config))
        if (
            not key.startswith('_')
            and (  # noqa: W503
                type(getattr(config, key))
                not in [
                    types.FunctionType,
                    types.ModuleType,
                    type,
                ]
            )
        )
    }
    logging.debug('Config:\n' + '\n'.join(f'  {key}: {val}' for key, val in config_dict.items()))

    # Inputs
    inputs_json = args.inputs
    inputs_file = args.inputs_file

    if not (inputs_json or inputs_file):
        raise ValueError('Either `--inputs` or `--inputs-file` must be specified.')

    inputs = Inputs()
    if inputs_json:
        inputs = Inputs.from_json(inputs_json)
    if inputs_file:
        inputs_from_file = Inputs.from_file(inputs_file)
        if inputs_json:
            inputs = Inputs.from_dict(inputs_from_file.to_dict() | inputs.to_dict())
        else:
            inputs = inputs_from_file
    logging.debug(f'Inputs:\n{pprint.pformat(inputs.to_dict(), indent=2)}')

    # Stylesheet
    css = None
    if args.stylesheet:
        css = read_file(args.stylesheet)

    # IPC params
    ipc_params_json = args.ipc
    ipc_params_file = args.ipc_file
    ipc_params = None
    if ipc_params_json:
        ipc_params = IpcParams.from_json(ipc_params_json)
    if ipc_params_file:
        ipc_params_from_file = IpcParams.from_file(ipc_params_file)
        if ipc_params:
            ipc_params = IpcParams.from_dict(ipc_params_from_file.to_dict() | ipc_params.to_dict())
        else:
            ipc_params = ipc_params_from_file
    if ipc_params:
        logging.debug(f'IPC params:\n{pprint.pformat(ipc_params.to_dict(), indent=2)}')

    return inputs, css, ipc_params


def main():
    _args = _parse_args()
    _inputs, _stylesheet, _ipc_params = _set_config_values(_args)
    _exit_code = show_dialog(_inputs, stylesheet=_stylesheet, ipc_params=_ipc_params, mode='return')
    logging.debug(f'App exiting with code {_exit_code} - {_exit_code.name}.')


if __name__ == '__main__':
    main()
