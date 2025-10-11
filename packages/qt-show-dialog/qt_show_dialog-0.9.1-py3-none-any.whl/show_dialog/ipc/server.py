import logging
import selectors
import socket
from typing import Callable

from .ipc_params import IpcParams
from .message import Message, MessageType


class IpcServer:
    def __init__(self, params: IpcParams, process: Callable[[Message], bool]):
        self.params = params
        self.process = process
        self.sel = selectors.DefaultSelector()
        self.loop = True

    def start(self):
        # Create a TCP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.params.host, self.params.port))
        server_socket.listen()
        server_socket.setblocking(False)  # Set the socket to non-blocking

        # Register the server socket to the selector
        self.sel.register(server_socket, selectors.EVENT_READ, self.accept)

        logging.debug(f'Server is listening at {self.params.host}:{self.params.port}')

        # Event loop
        try:
            while self.loop:
                logging.debug('Server loop.')
                events = self.sel.select(timeout=self.params.timeout)
                if not events:  # `events == []`
                    logging.warning('Server timeout.')
                    self.stop()
                for key, mask in events:
                    callback = key.data  # Get the callback function (`accept` or `read`)
                    callback(key.fileobj)
        except ConnectionResetError:
            logging.warning('Client disconnected.')
        except KeyboardInterrupt:
            logging.warning('Server is closing from keyboard interrupt.')
        finally:
            logging.debug('Server is closing.')
            self.sel.close()

    def stop(self):
        logging.debug('Server is stopping.')
        self.loop = False

    def accept(self, sock):
        """Callback function to handle incoming connections."""
        conn, addr = sock.accept()  # Accept the connection
        logging.debug(f'Server accepted connection from {addr}')
        conn.setblocking(False)  # Set the connection to non-blocking
        self.sel.register(conn, selectors.EVENT_READ, self.read)  # Register for read events

    def read(self, conn):
        """Callback function to handle client messages."""
        try:
            data = conn.recv(self.params.buffer_size)  # Receive data from the client
            if data:
                data_str = data.decode()
                logging.debug(f'Server received: {data_str}')
                message = Message.from_json(data.decode())
                self.send(conn, Message(MessageType.ACK))
                result = self.process(message)
                if not result:
                    self.stop()
            else:
                logging.debug('Server closing connection.')
                self.send(conn, Message(MessageType.TIMEOUT))
                self.sel.unregister(conn)
                conn.close()
        except BlockingIOError:
            pass  # Non-blocking, continue if there's no data

    def send(self, conn, message: Message):
        conn.sendall(message.to_json().encode())
