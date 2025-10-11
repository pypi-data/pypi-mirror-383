# qt-show-dialog

[![pypi](https://img.shields.io/pypi/v/qt-show-dialog.svg)](https://pypi.python.org/pypi/qt-show-dialog)
[![Project License - MIT](https://img.shields.io/pypi/l/qt-show-dialog.svg)](https://github.com/joaonc/show_dialog/blob/main/LICENSE.txt)

Easily show a dialog window for miscellaneous purposes
([features](https://joaonc.github.io/show_dialog/#features)).

----

The initial use case is to show instructions in manual steps in tests.

Uses [Qt 6](https://www.qt.io) and [Qt for Python](https://wiki.qt.io/Qt_for_Python), aka _PySide_,
which includes _Qt Designer_, a WYSIWYG UI editor.

## Getting started
Documentation: [https://joaonc.github.io/show_dialog](https://joaonc.github.io/show_dialog/)

### Installation
```
pip install qt-show-dialog
```

It can be used as a package or in the CLI with the `show_dialog` command.

Can also be used as an [executable app](https://joaonc.github.io/show_dialog/#executable-app) with
no dependencies (ie, no need for Python or a virtual environment).

### Example
[![show dialog](https://raw.githubusercontent.com/joaonc/show_dialog/main/docs/images/show_dialog_example.png)](https://joaonc.github.io/show_dialog/#example)

Inputs that generated the dialog 👆
```yaml
dialog_title: Manual step
title: Disconnect cable
description: |
    In this step we need to disconnect the power cable  
    and verify that the reserve battery gets discharged  
    within 5 seconds.
    
    ## Steps
    1. Disconnect power cable.  
       It's in the back.
    2. Wait 5 seconds.
    3. Check that reserve battery is empty.  
       See below for more info.

    ## Verifying battery is discharged
    There's a red light that goes off.
    
    **Do not touch** the button next to that light.
    
    More info on that light [here](#some-path).
description_md: true
timeout: 20
```
More info in documentation [here](https://joaonc.github.io/show_dialog/#example).
