import json
from typing import Any, List

from lime_python import SessionCompression, SessionEncryption, Transport
from websocket import WebsocketApp, enableTrace


class WebsocketTransport(Transport):
    """WebSocket transport implementation."""

    def __init__(self, trace_enabled: bool = False) -> None:
        super().__init__(SessionCompression.NONE, SessionEncryption.NONE)

        self.__websocket: WebsocketApp = None
        enableTrace(trace_enabled)

    def open(self, uri: str = None) -> None:  # noqa: D102
        if uri.startswith('wss://'):
            self.encryption = SessionEncryption.TLS
        else:
            self.encryption = SessionEncryption.NONE

        self.compression = SessionCompression.NONE

        self.__websocket = WebsocketApp(
            uri,
            subprotocols=['lime'],
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.__on_envelope
        )

    def close(self) -> None:  # noqa: D102
        self.__websocket.close()

    def send(self, envelope: dict) -> None:  # noqa: D102
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

    def on_open(self) -> None:
        """Handle on websocket open callback."""
        pass

    def on_close(self) -> None:
        """Handle on websocket close callback."""
        pass

    def on_error(self, err: Any) -> None:
        """Handle on websocket error callback.

        Args:
            err (Any): the exception
        """
        pass

    def __on_envelope(self, envelope: str) -> None:
        self.on_envelope(json.loads(envelope))
