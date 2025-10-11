from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from pytest_params import get_request_param, params

from src.show_dialog import Buttons, ExitCode, Inputs, ShowDialog
from src.show_dialog.ipc.client import IpcClient
from src.show_dialog.ipc.ipc_params import IpcParams
from src.show_dialog.ipc.message import Message, MessageType
from tests.libs import config


@pytest.fixture(scope='session')
def app():
    _app = QApplication([])
    yield _app


@pytest.fixture
def show_dialog(request, app, qtbot):
    inputs = get_request_param(request, 'inputs', Inputs())
    ipc_params = get_request_param(request, 'ipc_params')
    dialog = ShowDialog(app, inputs, ipc_params=ipc_params)
    qtbot.addWidget(dialog)

    yield dialog


@params(
    'show_dialog', [('dialog title', {'inputs': Inputs(dialog_title='foo bar')})], indirect=True
)
def test_dialog_title(show_dialog: ShowDialog):
    assert show_dialog.windowTitle() == 'foo bar'


@params('show_dialog', [('simple title', {'inputs': Inputs(title='foo bar')})], indirect=True)
def test_title(show_dialog: ShowDialog):
    assert show_dialog.title_label.text() == 'foo bar'


@params(
    'show_dialog',
    [('simple description', {'inputs': Inputs(description='foo bar')})],
    indirect=True,
)
def test_description(show_dialog: ShowDialog):
    assert show_dialog.description_label.text() == 'foo bar'


@params(
    'show_dialog, expected_description',
    [
        (
            'markdown description',
            {'inputs': Inputs(description='# Title\ntext', description_md=True)},
            '<h1>Title</h1>\n<p>text</p>',
        ),
        (
            'md multi line without nl2br',
            {'inputs': Inputs(description='line1\nline2', description_md=True)},
            '<p>line1\nline2</p>',  # No html break
        ),
        (
            'md multi line with nl2br',
            {
                'inputs': Inputs(
                    description='line1\nline2', description_md=True, description_md_nl2br=True
                )
            },
            '<p>line1<br />\nline2</p>',  # With html break
        ),
    ],
    indirect=['show_dialog'],
)
def test_description_md(show_dialog: ShowDialog, expected_description: str):
    assert show_dialog.description_label.text() == expected_description


@params(
    'show_dialog, expected_description',
    [
        (
            'single line',
            {'inputs': Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_02.yaml')},
            'This multiline text will transform into a single line.',
        ),
        (
            'single line, newline at end',
            {'inputs': Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_03.yaml')},
            'This multiline text will transform into a single line.\n',
        ),
        (
            'multi line',
            {'inputs': Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_04.yaml')},
            'This multiline text will\nretain its original newlines.',
        ),
        (
            'multi line, newline at end',
            {'inputs': Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_05.yaml')},
            'This multiline text will\nretain its original newlines.\n',
        ),
    ],
    indirect=['show_dialog'],
)
def test_description_multi_lines(show_dialog: ShowDialog, expected_description: str):
    assert show_dialog.description_label.text() == expected_description


@patch('PySide6.QtWidgets.QApplication.exit')
def test_pass_clicked(exit_mock, show_dialog: ShowDialog):
    """Clicking PASS button application exits with code 0."""
    QTest.mouseClick(show_dialog.pass_button, Qt.MouseButton.LeftButton)
    # exit_mock.assert_called_once_with(ExitCode.Pass)
    exit_mock.assert_any_call(ExitCode.Pass)


@patch('PySide6.QtWidgets.QApplication.exit')
def test_fail_clicked(exit_mock, show_dialog: ShowDialog):
    """Clicking FAIL button application exits with code 1."""
    QTest.mouseClick(show_dialog.fail_button, Qt.MouseButton.LeftButton)
    # exit_mock.assert_called_once_with(ExitCode.Fail)
    exit_mock.assert_any_call(ExitCode.Fail)


@pytest.mark.skip('Not working.')
@patch('PySide6.QtWidgets.QApplication.exit')
def test_pass_shortcut(exit_mock, show_dialog: ShowDialog):
    # key_event_press = QKeyEvent(
    #     QKeyEvent.Type.KeyPress, Qt.Key.Key_Q, Qt.KeyboardModifier.ControlModifier
    # )
    # key_event_release = QKeyEvent(
    #     QKeyEvent.Type.KeyRelease, Qt.Key.Key_Q, Qt.KeyboardModifier.ControlModifier
    # )
    #
    # show_dialog.app.postEvent(show_dialog, key_event_press)
    # show_dialog.app.postEvent(show_dialog, key_event_release)

    QTest.keyClick(show_dialog, Qt.Key.Key_P, Qt.KeyboardModifier.ControlModifier)
    exit_mock.assert_called_once_with(ExitCode.Pass)


@params(
    'show_dialog, expected_pass_fail_text',
    [
        (
            'custom text on buttons',
            {'inputs': Inputs.from_file(config.TEST_ASSETS_DIR / 'inputs/inputs_06.yaml')},
            ('Ok', 'Cancel'),
        ),
    ],
    indirect=['show_dialog'],
)
def test_pass_fail_buttons_text(show_dialog: ShowDialog, expected_pass_fail_text: tuple[str, str]):
    assert show_dialog.pass_button.text() == expected_pass_fail_text[0]
    assert show_dialog.fail_button.text() == expected_pass_fail_text[1]


@params(
    'show_dialog, expected_button_text',
    [
        ('default text', {'inputs': Inputs(buttons=Buttons.OK)}, 'Ok'),
        ('custom text', {'inputs': Inputs(buttons=Buttons.OK, pass_button_text='Foo')}, 'Foo'),
    ],
    indirect=['show_dialog'],
)
def test_ok_button(show_dialog: ShowDialog, expected_button_text: str):
    assert not show_dialog.fail_button.isVisible()
    assert show_dialog.pass_button.text() == expected_button_text


@params(
    'show_dialog, expected_pass_button_text, expected_fail_button_text',
    [
        ('defaults', {'inputs': Inputs()}, 'Pass', 'Fail'),
        ('ok cancel', {'inputs': Inputs(buttons=Buttons.OK_CANCEL)}, 'Ok', 'Cancel'),
        ('pass fail', {'inputs': Inputs(buttons=Buttons.PASS_FAIL)}, 'Pass', 'Fail'),
        ('yes no', {'inputs': Inputs(buttons=Buttons.YES_NO)}, 'Yes', 'No'),
        (
            'custom text',
            {
                'inputs': Inputs(
                    buttons=Buttons.OK_CANCEL, pass_button_text='Foo', fail_button_text='Bar'
                )
            },
            'Foo',
            'Bar',
        ),
    ],
    indirect=['show_dialog'],
)
def test_two_buttons(
    show_dialog: ShowDialog, expected_pass_button_text: str, expected_fail_button_text: str
):
    assert show_dialog.pass_button.text() == expected_pass_button_text
    assert show_dialog.fail_button.text() == expected_fail_button_text


@params(
    'show_dialog',
    [
        ('no timeout - default', {'inputs': Inputs()}),
        ('no timeout - set to 0', {'inputs': Inputs(timeout=0)}),
    ],
    indirect=True,
)
def test_timeout_no_timeout(show_dialog: ShowDialog):
    """Timeout UI should not appear if there's no timeout."""
    assert not show_dialog.timeout_progress_bar.isVisible()
    assert not show_dialog.timeout_increase_button.isVisible()


@params(
    'show_dialog',
    [
        (
            'ipc server',
            {
                'inputs': Inputs(title='ipc'),
                'ipc_params': IpcParams(host='localhost', port=12345, timeout=5),
            },
        )
    ],
    indirect=True,
)
@pytest.mark.skip('Need to finish implementing IPC functionality.')
def test_ipc(show_dialog: ShowDialog):
    client = IpcClient(show_dialog.ipc_params)  # type: ignore
    client.send(Message(MessageType.PASS))
    client.close()
    assert False, 'ZZZZ'
