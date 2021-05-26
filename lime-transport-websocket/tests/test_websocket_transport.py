import threading
from pytest_mock import MockerFixture
from pytest import fixture, mark
from .helpers import MESSAGES, WebsocketLimeService
from src import WebsocketTransport
from time import sleep


class TestWebsocketTransport:

    @fixture(autouse=True)
    def before_each(self) -> None:
        self.server = WebsocketLimeService(8124)
        serve = self.server.socket.run_forever
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=serve)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

    @mark.asyncio
    async def test_open(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy = mocker.spy(target, 'on_open')

        # Act
        await target.open_async('ws://127.0.0.1:8124/')
        sleep(0.5)

        # Assert
        spy.assert_called_once()

    def test_close(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy = mocker.spy(target, 'on_close')

        # Act
        target.open_async('ws://127.0.0.1:8124/')
        sleep(0.5)
        target.close_async()

        # Assert
        spy.assert_called_once()

    def test_send_and_receive_envelope(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy_receive = mocker.spy(target, 'on_envelope')

        # Act
        target.open_async('ws://127.0.0.1:8124/')
        sleep(0.5)
        target.send({'content': 'ping'})
        sleep(0.5)

        # Assert
        spy_receive.assert_called_once_with(MESSAGES['pong'])

    def test_receive_broadcast_messages(self, mocker: MockerFixture) -> None:
        # Arrange
        target1 = self.get_target()
        target2 = self.get_target()

        spy_receive1 = mocker.spy(target1, 'on_envelope')
        spy_receive2 = mocker.spy(target2, 'on_envelope')

        # Act
        target1.open_async('ws://127.0.0.1:8124/')
        target2.open_async('ws://127.0.0.1:8124/')
        sleep(0.5)
        self.server.broadcast(MESSAGES['pong'])
        sleep(0.5)

        # Assert
        spy_receive1.assert_called_once_with(MESSAGES['pong'])
        spy_receive2.assert_called_once_with(MESSAGES['pong'])

    def get_target(self) -> WebsocketTransport:
        return WebsocketTransport()
