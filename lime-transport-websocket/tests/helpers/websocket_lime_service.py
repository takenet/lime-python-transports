import json
from lime_python import Envelope, SessionState, UriTemplates
from websocket_server import WebsocketServer
from .test_envelopes import COMMANDS, MESSAGES, NOTIFICATIONS, SESSIONS


class WebsocketLimeService:
    """Websocket server."""

    def __init__(self, port: int) -> None:
        self.socket = WebsocketServer(port)
        self.socket.set_fn_message_received(self.on_message)

    def send_envelope(self, client, envelope: dict) -> None:  # noqa: D102
        self.socket.send_message(client, json.dumps(envelope))

    def broadcast(self, envelope: dict) -> None:  # noqa: D102
        self.socket.send_message_to_all(json.dumps(envelope))

    def on_message(self, client, server, envelope: str) -> None:  # noqa: D102, WPS231, E501
        envelope: dict = json.loads(envelope)

        if Envelope.is_session(envelope):
            if envelope['state'] == SessionState.NEW:
                self.send_envelope(client, SESSIONS['authenticating'])
                return
            if envelope['state'] == SessionState.AUTHENTICATING:
                self.send_envelope(client, SESSIONS['established'])
                return

        if Envelope.is_command(envelope):
            if envelope['uri'] == UriTemplates.PING:
                self.send_envelope(client, COMMANDS['ping_response'](envelope))
                return

        if Envelope.is_message(envelope):
            if envelope['content'] == 'ping':
                self.send_envelope(client, MESSAGES['pong'])
                return

        if Envelope.is_notification(envelope):
            if envelope['event'] == 'ping':
                self.send_envelope(client, NOTIFICATIONS['pong'])
                return
