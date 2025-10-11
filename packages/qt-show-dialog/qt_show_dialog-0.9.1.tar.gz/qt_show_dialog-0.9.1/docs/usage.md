# Usage
## Library
**TODO**

### Logging
**TODO**

## Shortcuts
The following shortcuts are available:

| Shortcut   |                  |
|------------|------------------|
| `Ctrl`+`Q` | Exit as failure  |
| `Ctrl`+`P` | Exit as pass     |
| `+`        | Increase timeout |

!!! Note

    The `Esc` key is disabled in order to prevent accidentally dismissing the dialog.

## Executable
This section applies to both the executable app and the CLI script after pip installing the package.

**TODO**

### Exit codes
`0` represents success, otherwise failure.

| Exit code |                                                                                                                                  |
|:---------:|----------------------------------------------------------------------------------------------------------------------------------|
|    `0`    | One of:<li>`Pass` button was clicked.<li>Timeout occurred and `timeout_pass` is `True` in inputs.<li>`Ctrl+P` shortcut was used. |
|    `1`    | Unknown error, likely from an uncaught exception.                                                                                |
|    `2`    | `Fail` button was clicked.                                                                                                       |
|    `3`    | One of:<li>Dialog was closed with the `X` button.<li>`Ctrl+Q` shortcut was used.                                                 |
|    `4`    | Timeout occurred and `timeout_pass` is `False` in inputs.                                                                        |

These exit codes are represented in the
[`ExitCode`](https://github.com/joaonc/show_dialog/blob/main/src/show_dialog/exit_code.py) class.
