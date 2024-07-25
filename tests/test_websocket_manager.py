import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import json
from app.websocket_manager import WebSocketManager
from app import socketio


class TestWebSocketManager(unittest.TestCase):
    def setUp(self):
        self.ws_manager = WebSocketManager(socketio)
        self.ws_manager.db_manager = MagicMock()
        self.ws_manager.socketio.emit = MagicMock()

    @patch('app.websocket_manager.asyncio.run_coroutine_threadsafe', new_callable=MagicMock)
    @patch('app.websocket_manager.websockets.connect', new_callable=AsyncMock)
    def test_subscribe(self, mock_connect, mock_run_coroutine_threadsafe):
        self.ws_manager.connection = AsyncMock()
        self.ws_manager.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_manager.loop)

        self.ws_manager.subscribe('BTCUSD@trade')
        self.assertIn('BTCUSD@trade', self.ws_manager.subscriptions)

        message = {
            "method": "SUBSCRIBE",
            "params": ['BTCUSD@trade'],
            "id": 1
        }
        self.ws_manager.connection.send.assert_called_with(json.dumps(message))

    @patch('app.websocket_manager.asyncio.run_coroutine_threadsafe', new_callable=MagicMock)
    @patch('app.websocket_manager.websockets.connect', new_callable=AsyncMock)
    def test_unsubscribe(self, mock_connect, mock_run_coroutine_threadsafe):
        self.ws_manager.connection = AsyncMock()
        self.ws_manager.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_manager.loop)

        self.ws_manager.subscriptions = ['BTCUSD@trade']
        self.ws_manager.unsubscribe('BTCUSD@trade')
        self.assertNotIn('BTCUSD@trade', self.ws_manager.subscriptions)

        message = {
            "method": "UNSUBSCRIBE",
            "params": ['BTCUSD@trade'],
            "id": 2
        }
        self.ws_manager.connection.send.assert_called_with(json.dumps(message))


if __name__ == "__main__":
    unittest.main()
