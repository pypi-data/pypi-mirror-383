# `.../ui/forms` folder
The files in this folder are created with PySide tools and should not be edited manually or with
linters.

## `ui_*.py` files
Generated from the `.ui` files under `/assets/ui`.

Uses the tool `pyside6-uic` and generated with the command
```
inv ui.py -f <filename>

# Ex
inv ui.py -f show_dialog
```

`inv --help ui.py` for more details.

## `resources_rc.py` file
Qt [resources](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QResource.html) added in the UI
builder and manually as well.

Generated from the `.qrc` files under `/assets`.  
More info on `.qrc` files
[here](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/qrcfiles.html).

Uses the tool `pyside6-rcc` and generated with the command
```
inv ui.rc
```
