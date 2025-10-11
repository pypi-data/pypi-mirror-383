import logging
import threading
import time

import markdown
import qdarkstyle
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QDialog
from qdarkstyle.dark.palette import DarkPalette
from qdarkstyle.light.palette import LightPalette

from ..exit_code import ExitCode
from ..inputs import Buttons, Inputs, Theme
from ..ipc.ipc_params import IpcParams
from ..ipc.message import Message, MessageType
from ..ipc.server import IpcServer
from ..utils_qt import set_layout_visibility
from .forms.ui_show_dialog import Ui_ShowDialog


class ShowDialog(QDialog, Ui_ShowDialog):
    def __init__(
        self,
        app: QApplication,
        inputs: Inputs,
        *,
        stylesheet: str | None = None,
        ipc_params: IpcParams | None = None,
    ):
        super().__init__()
        self.app = app
        self.stylesheet = stylesheet
        self.setupUi(self)
        self.inputs = inputs
        self.ipc_params = ipc_params
        self.timer = None

        # UI adjustments
        local_stylesheet = ''
        """Stylesheet modifications that depend on inputs."""

        self.title_label.setText(self.inputs.title)
        if self.inputs.description_md:
            if self.inputs.description_md_nl2br:
                description = markdown.markdown(self.inputs.description, extensions=['nl2br'])
            else:
                description = markdown.markdown(self.inputs.description)
            logging.debug(f'Description converted to HTML:\n{description}')
        else:
            description = self.inputs.description
        self.description_label.setText(description)
        if self.inputs.dialog_title:
            self.setWindowTitle(self.inputs.dialog_title)

        # Buttons
        if inputs.buttons == Buttons.OK:
            # These settings may be overridden further below from `inputs`
            self.fail_button.setVisible(False)
            self.pass_button.setText(Buttons.OK)
            self.pass_button.setIcon(QIcon())
            local_stylesheet += 'QPushButton#pass_button { color : black; }'
        else:
            pass_text, fail_text = inputs.buttons.split('/')
            self.pass_button.setText(pass_text)
            self.fail_button.setText(fail_text)

        if self.inputs.pass_button_text:
            self.pass_button.setText(self.inputs.pass_button_text)
        if self.inputs.pass_button_icon:
            icon = QIcon(self.inputs.pass_button_icon)
            if not icon:
                logging.warning(
                    f'Icon image for PASS button not found: {self.inputs.pass_button_icon}'
                )
            self.pass_button.setIcon(icon)
        if self.inputs.fail_button_text:
            self.fail_button.setText(self.inputs.fail_button_text)
        if self.inputs.fail_button_icon:
            icon = QIcon(self.inputs.fail_button_icon)
            if not icon:
                logging.warning(
                    f'Icon image for FAIL button not found: {self.inputs.fail_button_icon}'
                )
            self.fail_button.setIcon(icon)

        # Timeout
        if self.inputs.timeout:
            self.timeout_increase_button.setIconSize(self.timeout_increase_button.size())
            self.timeout_increase_button.clicked.connect(self.timeout_increase_clicked)
            self.timeout_progress_bar.setMinimum(0)
            self.timeout_progress_bar.setMaximum(self.inputs.timeout)
            self.timeout_progress_bar.setValue(self.inputs.timeout)
            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.timer_timeout)
            self.timer.start()
            if self.inputs.timeout_text:
                self.timeout_progress_bar.setFormat(self.inputs.timeout_text)
            else:
                self.timeout_progress_bar.setTextVisible(False)
        else:
            set_layout_visibility(self.timeout_h_layout, False)

        # Stylesheet
        logging.getLogger('qdarkstyle').setLevel(logging.ERROR)  # Disable `qdarkstyle` logging
        stylesheet_app = {
            Theme.Light: qdarkstyle.load_stylesheet(palette=LightPalette),
            Theme.Dark: qdarkstyle.load_stylesheet(palette=DarkPalette),
            Theme.System: '',
        }[inputs.theme]
        if self.stylesheet:
            # Combine the two stylesheets
            stylesheet_app += self.stylesheet + local_stylesheet
        self.app.setStyleSheet(stylesheet_app)

        # UI bindings
        self.pass_button.clicked.connect(self.pass_clicked)
        self.fail_button.clicked.connect(lambda: self.fail_clicked(ExitCode.Fail))
        self.exit_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.exit_shortcut.activated.connect(lambda: self.fail_clicked(ExitCode.Cancel))
        self.pass_shortcut = QShortcut(QKeySequence('Ctrl+P'), self)
        self.pass_shortcut.activated.connect(self.pass_clicked)
        self.timeout_shortcut = QShortcut(QKeySequence('+'), self)
        self.timeout_shortcut.activated.connect(self.timeout_increase_clicked)

        # Inter-Process Communication server
        self.ipc_server = self.ipc_thread = None
        if self.ipc_params is not None:
            self.ipc_server = IpcServer(self.ipc_params, self.process_ipc_message)
            self.ipc_thread = threading.Thread(
                target=self.ipc_server.start, name='show_dialog_ipc_server'
            )
            self.ipc_thread.start()

    def process_ipc_message(self, message: Message) -> bool:
        if message.type is MessageType.TIMEOUT:
            self.timeout()
            return False
        elif message.type is MessageType.PASS:
            self.pass_clicked()
            return False
        elif message.type is MessageType.FAIL:
            self.fail_clicked(ExitCode.Timeout)
            return False
        return True

    def exit(self, exit_code: ExitCode):
        if self.ipc_server:
            self.ipc_server.stop()
            timeout = 3.0
            timeout_step = 0.3
            while self.ipc_thread.is_alive():  # type: ignore
                time.sleep(timeout_step)
                timeout -= timeout_step
                if timeout <= 0:
                    raise ValueError('Error stopping IPC server.')
            logging.debug('IPC server sopped successfully.')

        logging.debug(f'Exiting with code {exit_code.value}: {exit_code.name}.')
        self.app.exit(int(exit_code))

    def resizeEvent(self, event):
        self.pass_button.setIconSize(self.pass_button.size())
        self.fail_button.setIconSize(self.fail_button.size())

    def closeEvent(self, event):
        """
        When closing the app (``X`` button), mark as fail instead of pass.
        """
        self.fail_clicked(ExitCode.Cancel)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # Disable exiting the app when pressing escape.
            # This avoids passing the step unintentionally by accidentally pressing escape.
            pass
        else:
            super().keyPressEvent(event)

    def timeout(self):
        """Timeout occurred. Process it."""
        logging.debug('Timeout.')
        if self.inputs.timeout_pass:
            self.pass_clicked()
        else:
            self.fail_clicked(ExitCode.Timeout)

    def timer_timeout(self):
        new_value = self.timeout_progress_bar.value() - self.timer.interval() / 1000
        self.timeout_progress_bar.setValue(new_value)
        if new_value <= 0:
            self.timeout()

    def timeout_increase_clicked(self):
        timeout_increase = 10
        new_value = self.timeout_progress_bar.value() + timeout_increase
        if new_value > self.timeout_progress_bar.maximum():
            self.timeout_progress_bar.setMaximum(new_value)
        self.timeout_progress_bar.setValue(new_value)

    def pass_clicked(self):
        # Using `QApplication.exit(0)` to enable testing exit code.
        self.close()
        self.exit(ExitCode.Pass)

    def fail_clicked(self, exit_code: ExitCode):
        self.close()
        self.exit(exit_code)
