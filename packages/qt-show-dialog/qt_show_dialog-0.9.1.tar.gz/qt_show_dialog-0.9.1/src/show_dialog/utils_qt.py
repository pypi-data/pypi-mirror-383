from PySide6.QtCore import QDir, QFile, QTextStream
from PySide6.QtWidgets import QLayout


def list_resources(base_path: str = ':/', recursive: bool = False) -> list[str]:
    d = QDir(base_path)
    if not d.exists():
        raise NotADirectoryError(base_path)

    if recursive:
        raise RuntimeError('Recursion not working: https://github.com/joaonc/show_dialog/issues/16')
        # dirs = d.entryList(QDir.Filter.Dirs)
        # for subdir in dirs:
        #     entries += list_resources(subdir, True)

    # Note: The filter `QDir.Filter.Files` doesn't work on python 3.11
    #       https://github.com/joaonc/show_dialog/issues/16
    # entries = d.entryList(QDir.Filter.Files)
    entries = d.entryList()

    # The `if` condition is a workaround for the issue above
    return [f'{base_path}/{entry}' for entry in entries if entry not in ['.', '..']]


def read_file(file_path):
    """
    Read both regular files (from a path) and resource files (file inside a resource).
    """
    file = QFile(file_path)
    if not file.exists():
        raise FileNotFoundError(file_path)
    if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        raise RuntimeError(f'Cannot open file: `{file_path}`')
    stream = QTextStream(file)
    content = stream.readAll()
    file.close()

    return content


def set_layout_visibility(layout: QLayout, visible: bool) -> None:
    """
    Set visibility for all widgets and layouts within the given layout.
    """
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if isinstance(item, QLayout):
            set_layout_visibility(item, visible)
        else:
            if item is not None and ((widget := item.widget()) is not None):
                widget.setVisible(visible)
