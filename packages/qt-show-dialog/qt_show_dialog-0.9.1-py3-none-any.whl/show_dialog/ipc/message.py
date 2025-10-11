import json
import random
import string
import time
from dataclasses import asdict, dataclass, field
from enum import Enum

BASE62_CHARS = string.digits + string.ascii_letters
"""Characters used in base62 encoding."""
BASE62_MAP = {char: index for index, char in enumerate(BASE62_CHARS)}


class MessageType(str, Enum):
    MESSAGE = 'message'
    TIMEOUT = 'timeout'
    ACK = 'ack'
    PASS = 'pass'
    FAIL = 'fail'


class MessageId:
    """
    Time based ID.
    Timestamp in milliseconds.
    """

    _num_random_chars = 2
    """Additional random chars in case ID's are generated with the exact same timestamp."""

    def __init__(self, id: str = ''):
        if id:
            self.id = id
            self.timestamp = self._decode_base62(id[: -self._num_random_chars])
        else:
            self.timestamp = int(time.time() * 1000)
            self.id = self._encode_base62(self.timestamp)
            self.id += ''.join(random.choices(BASE62_CHARS, k=self._num_random_chars))

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}')"

    @staticmethod
    def _encode_base62(num):
        base62 = []
        while num:
            num, remainder = divmod(num, 62)
            base62.append(BASE62_CHARS[remainder])

        # Reverse to get the correct order
        return ''.join(reversed(base62))

    @staticmethod
    def _decode_base62(base62_str: str):
        num = 0
        for char in base62_str:
            num = num * 62 + BASE62_MAP[char]
        return num


@dataclass
class Message:
    type: str | MessageType
    message: str = ''
    data: dict = field(default_factory=dict)
    id: MessageId = MessageId()

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = MessageType(self.type)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        obj_dict = self.to_dict()
        if not self.message:
            del obj_dict['message']
        if not self.data:
            del obj_dict['data']
        obj_dict['id'] = str(obj_dict['id'])
        return json.dumps(obj_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        obj_dict = json.loads(json_str)
        return cls(**obj_dict)
