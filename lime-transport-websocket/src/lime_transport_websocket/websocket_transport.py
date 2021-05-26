from asyncio import Future
from asyncio.events import get_running_loop
import json
from threading import Thread
from typing import Any, Callable, List
from lime_python import SessionCompression, SessionEncryption, Transport
from websocket import WebSocketApp, enableTrace


class WebsocketTransport(Transport):
    """WebSocket transport implementation."""

    def __init__(self, trace_enabled: bool = False) -> None:
        super().__init__(SessionCompression.NONE, SessionEncryption.NONE)

        self.__websocket: WebSocketApp = None
        self.__connect_resolve: Callable = None
        self.__disconnect_resolve: Callable = None
        self.is_connected = False
        enableTrace(trace_enabled)

    def open_async(self, uri: str = None) -> Future:  # noqa: D102
        if self.is_connected:
            raise ValueError('Cannot open an already open connection')
        loop = get_running_loop()
        future = loop.create_future()
        self.__connect_resolve = future.set_result

        if uri.startswith('wss://'):
            self.encryption = SessionEncryption.TLS
        else:
            self.encryption = SessionEncryption.NONE

        self.compression = SessionCompression.NONE

        self.__websocket = WebSocketApp(
            uri,
            on_open=self.__on_open,
            on_close=self.__on_close,
            on_error=self.on_error,
            on_message=self.__on_envelope
        )
        self.__run()
        return future

    def close_async(self) -> Future:  # noqa: D102
        if not self.is_connected:
            raise ValueError('Cannot close a non open connection')
        loop = get_running_loop()
        future = loop.create_future()
        self.__disconnect_resolve = future.set_result
        self.__websocket.close()
        return future

    def send(self, envelope: dict) -> None:  # noqa: D102
        if not self.is_connected:
            raise ValueError('Cannot send a message while disconnected')
        self.__websocket.send(json.dumps(envelope))

    def get_supported_compression(self) -> List[str]:  # noqa: D102
        return [SessionCompression.NONE]

    def set_compression(self, compression: str) -> None:  # noqa: D102
        pass

    def get_supported_encryption(self) -> List[str]:  # noqa: D102
        return [SessionEncryption.TLS, SessionEncryption.NONE]

    def set_encryption(self, encryption: str) -> None:  # noqa: D102
        pass

    def on_envelope(self, envelope: dict) -> None:  # noqa: D102
        pass

    def on_open(self, ws) -> None:
        """Handle on websocket open callback."""  # noqa: DAR101
        pass

    def on_close(self, ws, _, __) -> None:  # noqa: WPS123
        """Handle on websocket close callback."""  # noqa: DAR101
        pass

    def on_error(self, ws, err: Any) -> None:
        """Handle on websocket error callback.

        Args:
            err (Any): the exception
        """  # noqa: DAR101
        pass

    def __on_open(self, ws) -> None:
        self.__connect_resolve(None)
        self.is_connected = True
        self.on_open()

    def __on_close(self, ws) -> None:
        self.__disconnect_resolve(None)
        self.is_connected = False
        self.on_close()

    def __run(self) -> None:
        serve = self.__websocket.run_forever
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = Thread(target=serve)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

    def __on_envelope(self, ws, envelope: str) -> None:
        self.on_envelope(json.loads(envelope))
