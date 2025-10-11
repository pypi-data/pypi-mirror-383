import json

from pytest_params import params

from src.show_dialog.ipc.message import Message, MessageId, MessageType


class TestMessageId:
    def test_id_generation(self):
        m1 = MessageId()
        m2 = MessageId()
        assert m1.id != m2.id


class TestMessage:
    @params(
        'message, expected',
        (
            ('type only', Message(MessageType.MESSAGE), '{"type": "message"}'),
            ('type as str', Message('timeout'), '{"type": "timeout"}'),
            (
                'with message',
                Message(MessageType.MESSAGE, message='foo'),
                '{"type": "message", "message": "foo"}',
            ),
            (
                'with data',
                Message(MessageType.MESSAGE, data={'foo': 1}),
                '{"type": "message", "data": {"foo": 1}}',
            ),
            (
                'with message and data',
                Message(MessageType.MESSAGE, message='foo', data={'bar': 'baz'}),
                '{"type": "message", "message": "foo", "data": {"bar": "baz"}}',
            ),
        ),
    )
    def test_to_json(self, message, expected):
        """
        Verify the ``to_json()`` method.
        ``id`` is not compared.
        """
        message_json = message.to_json()
        message_dict = json.loads(message_json)
        del message_dict['id']
        message_json_no_id = json.dumps(message_dict)
        assert message_json_no_id == expected

    def test_to_json_with_id(self):
        message_id = MessageId()
        message = Message(MessageType.ACK, message='foo', data={'bar': 0}, id=message_id)
        assert (
            message.to_json()
            == f'{{"type": "ack", "message": "foo", "data": {{"bar": 0}}, "id": "{message_id}"}}'
        )
