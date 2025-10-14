import socket
from threading import Thread
import base64
import json
import sys
from typing import Callable

from keyboardsounds.external_api.__connection_handler import _ConnectionHandler


class ExternalAPI:
    def __init__(
        self, socket: socket.socket, on_command: Callable[[dict], None]
    ) -> None:
        self.__socket = socket
        self.__continue = True
        self.__on_command = on_command
        self.__port = int(socket.getsockname()[1])
        self.__thread = None

    def listen(self) -> None:
        if self.__thread is None:
            self.__thread = Thread(target=self.__listen)
            self.__thread.daemon = True
            self.__thread.start()

    def block(self):
        if self.__thread is not None:
            while self.__continue:
                try:
                    self.__thread.join(1)
                except KeyboardInterrupt:
                    sys.exit(0)

    def stop(self) -> None:
        if self.__thread is not None:
            # Signal the listener loop to stop
            self.__continue = False
            # Nudge the blocking accept() by connecting to the local port
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.2)
                    s.connect(("localhost", self.__port))
            except Exception:
                pass
            # Join the thread now that accept() should have returned
            self.__thread.join()
            self.__thread = None

    def port(self) -> int:
        return self.__port

    def __listen(self):
        self.__socket.listen(9)
        print(f"external API listening on localhost:{self.__port}")

        connection_handlers: list[tuple[_ConnectionHandler, Thread]] = []

        while self.__continue:
            try:
                conn, _ = self.__socket.accept()
            except OSError:
                # Socket likely closed during stop(); exit if we're stopping
                if not self.__continue:
                    break
                else:
                    continue
            connection = _ConnectionHandler(conn=conn, on_command=self.__on_command)
            thread = Thread(target=connection.handle_connection)
            thread.daemon = True
            thread.start()
            connection_handlers.append((connection, thread))

        for connect, thread in connection_handlers:
            connect.stop()
            thread.join()

        self.__socket.close()
