from asyncio import sleep
from pytest_mock import MockerFixture
from pytest import fixture, mark
from .helpers import MESSAGES, WebsocketLimeService
from src import WebsocketTransport


class TestWebsocketTransport:

    @fixture(autouse=True)
    @mark.asyncio
    async def server_test(self) -> None:
        server = WebsocketLimeService(8124)
        await server.open_async()

        yield server

        await server.close_async()

    @mark.asyncio
    async def test_open(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy = mocker.spy(target, 'on_open')

        # Act
        await target.open_async('ws://127.0.0.1:8124/')

        # Assert
        spy.assert_called_once()

    @mark.asyncio
    async def test_close_async(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy = mocker.spy(target, 'on_close')

        # Act
        await target.open_async('ws://127.0.0.1:8124/')
        await target.close_async()

        # Assert
        spy.assert_called_once()

    @mark.asyncio
    async def test_send_and_receive_envelope(self, mocker: MockerFixture) -> None:
        # Arrange
        target = self.get_target()

        spy_receive = mocker.spy(target, 'on_envelope')

        # Act
        await target.open_async('ws://127.0.0.1:8124/')
        target.send({'content': 'ping'})
        await sleep(0.5)

        # Assert
        spy_receive.assert_called_once_with(MESSAGES['pong'])

    @mark.asyncio
    async def test_receive_broadcast_messages(self, mocker: MockerFixture, server_test: WebsocketLimeService) -> None:
        # Arrange
        target1 = self.get_target()
        target2 = self.get_target()

        spy_receive1 = mocker.spy(target1, 'on_envelope')
        spy_receive2 = mocker.spy(target2, 'on_envelope')

        # Act
        await target1.open_async('ws://127.0.0.1:8124/')
        await target2.open_async('ws://127.0.0.1:8124/')
        await server_test.broadcast_async(MESSAGES['pong'])
        await sleep(0.5)

        # Assert
        spy_receive1.assert_called_once_with(MESSAGES['pong'])
        spy_receive2.assert_called_once_with(MESSAGES['pong'])

    def get_target(self) -> WebsocketTransport:
        return WebsocketTransport()
