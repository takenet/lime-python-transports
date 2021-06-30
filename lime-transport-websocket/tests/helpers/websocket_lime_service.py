import json
from asyncio import wait
from typing import Set

from lime_python import (Command, Envelope, Message,  # noqa: E501
                         Notification, Session, SessionState)
from websockets.server import WebSocketServer, WebSocketServerProtocol, serve

from .test_envelopes import COMMANDS, MESSAGES, NOTIFICATIONS, SESSIONS


class WebsocketLimeService:
    """Websocket server."""

    def __init__(self, port: int) -> None:
        self.port = port
        self.websocket: WebSocketServer = None
        self.clients: Set[WebSocketServerProtocol] = set()

    async def open_async(self) -> None:  # noqa: D102
        self.websocket = await serve(
            self.__consumer_handler,
            '127.0.0.1',
            self.port,
            subprotocols=['lime']
        )

    async def close_async(self) -> None:  # noqa: D102
        self.websocket.close()
        await self.websocket.wait_closed()

    async def send_envelope_async(  # noqa: D102
        self,
        client: WebSocketServerProtocol,
        envelope: dict
    ) -> None:
        await client.send(json.dumps(envelope))

    async def broadcast_async(self, envelope: dict) -> None:  # noqa: D102
        if self.clients:
            await wait(
                [
                    self.send_envelope_async(client, envelope)
                    for client in self.clients
                ]
            )

    async def on_message_async(  # noqa: D102, WPS231
        self,
        client: WebSocketServerProtocol,
        envelope: str
    ) -> None:
        envelope: dict = json.loads(envelope)

        if Envelope.is_session(envelope):
            session: Session = Session.from_json(envelope)
            if session.state == SessionState.NEW:
                await self.send_envelope_async(
                    client,
                    SESSIONS.authenticating
                )
                return
            if session.state == SessionState.AUTHENTICATING:
                await self.send_envelope_async(
                    client,
                    SESSIONS.established
                )
                return

        if Envelope.is_command(envelope):
            command: Command = Command.from_json(envelope)
            if command.uri == '/ping':
                await self.send_envelope_async(
                    client,
                    COMMANDS.ping_response(command)
                )
                return

        if Envelope.is_message(envelope):
            message: Message = Message.from_json(envelope)
            if message.content == 'ping':
                await self.send_envelope_async(
                    client,
                    MESSAGES.pong
                )
                return

        if Envelope.is_notification(envelope):
            notification: Notification = Notification.from_json(envelope)
            if notification.event == 'ping':
                await self.send_envelope_async(
                    client,
                    NOTIFICATIONS.pong
                )
                return

    async def __consumer_handler(
        self,
        websocket: WebSocketServerProtocol,
        path: str
    ) -> None:
        self.clients.add(websocket)
        async for message in websocket:
            await self.on_message_async(websocket, message)
