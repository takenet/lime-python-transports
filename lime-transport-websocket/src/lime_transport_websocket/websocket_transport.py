import json
import logging
from asyncio import ensure_future
from typing import Any, List
from lime_python import SessionCompression, SessionEncryption, Transport
from websockets.client import WebSocketClientProtocol, connect
from websockets.exceptions import ConnectionClosed


class WebSocketTransport(Transport):
    """WebSocket transport implementation."""

    def __init__(self, is_trace_enabled: bool = False) -> None:
        super().__init__(SessionCompression.NONE, SessionEncryption.NONE)

        self.is_trace_enabled = is_trace_enabled
        self.logger = logging.getLogger()
        self.websocket: WebSocketClientProtocol = None

    async def open_async(self, uri: str = None) -> None:  # noqa: D102
        if self.websocket and self.websocket.open:
            err = ValueError('Cannot open an already open connection')
            self.on_error(err)
            raise err

        if uri.startswith('wss://'):
            self.encryption = SessionEncryption.TLS
        else:
            self.encryption = SessionEncryption.NONE

        self.compression = SessionCompression.NONE

        self.websocket = await connect(uri, subprotocols=['lime'])
        self.on_open()

        ensure_future(self.__message_handler_async())

    async def close_async(self) -> None:  # noqa: D102
        await self.websocket.close()
        self.on_close()

    def send(self, envelope: dict) -> None:  # noqa: D102
        self.__ensure_is_open()

        envelope_str = json.dumps(envelope)
        if self.is_trace_enabled:
            self.logger.debug(f'WebSocket SEND: {envelope_str}')

        ensure_future(self.websocket.send(envelope_str))

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

    def on_close(self) -> None:  # noqa: WPS123
        """Handle on websocket close callback."""
        pass

    def on_error(self, err: Any) -> None:
        """Handle on websocket error callback.

        Args:
            err (Any): the exception
        """
        pass

    def __ensure_is_open(self) -> None:
        if not self.websocket or not self.websocket.open:
            err = ValueError('The connection is not open')
            self.on_error(err)
            raise err

    async def __message_handler_async(self) -> None:
        try:
            while True:  # noqa: WPS457
                message = await self.websocket.recv()
                self.__on_envelope(message)
        except ConnectionClosed:
            if self.is_trace_enabled:
                self.logger.debug(
                    'Stopped receiving messages due to closed connection'
                )

    def __on_envelope(self, envelope: str) -> None:
        if self.is_trace_enabled:
            self.logger.debug(f'WebSocket RECEIVE: {envelope}')
        self.on_envelope(json.loads(envelope))
