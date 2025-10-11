import logging
import socket

from .ipc_params import IpcParams
from .message import Message, MessageType


class IpcClient:
    def __init__(self, params: IpcParams):
        self.params = params

        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(self.params.timeout)

        # Connect to the server
        self.client_socket.connect((self.params.host, self.params.port))

    def send(self, message: Message):
        """Send a message ot the server."""
        try:
            message_json = message.to_json()
            logging.debug(f'Client sending: {message_json}')
            self.client_socket.sendall(message_json.encode())

            # Receive a response from the server
            response = self.client_socket.recv(self.params.buffer_size).decode()
            message_response = Message.from_json(response)
            logging.debug(f'Client received: {message_response.to_json()}')
        except Exception as e:
            logging.error(e)
            self.close()

    def close(self):
        """Close the connection"""
        self.client_socket.close()
        logging.debug('Client closed the connection.')


if __name__ == '__main__':
    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(
        description="IPC client for show-dialog.", formatter_class=RawTextHelpFormatter
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
        default='debug',
        help='Log level to use.',
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.getLevelName(args.log_level.upper()))

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
    if not ipc_params:
        raise ValueError('Either `--ipc` or `--ipc-file` must be specified.')

    print(f'Connecting to Show Dialog server at {ipc_params.host}:{ipc_params.port}.')
    client = IpcClient(ipc_params)

    commands = {'0': 'Exit client'}
    commands |= {f'{i+1}': message_type for i, message_type in enumerate(MessageType)}
    print('Select one of the commands:\n' + '\n'.join(f'{k}: {v}' for k, v in commands.items()))
    while (command := input('> ').strip()) != '0':
        message = Message(commands[command])
        client.send(message)
