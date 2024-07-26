import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.websocket_manager import WebSocketManager
import json


@pytest.fixture
def mock_socketio():
    return MagicMock()


@pytest.fixture
def mock_db_manager():
    with patch('app.websocket_manager.DatabaseManager', autospec=True) as mock:
        yield mock


@pytest.fixture
def websocket_manager(mock_socketio, mock_db_manager):
    return WebSocketManager(mock_socketio)


def test_start(websocket_manager):
    with patch('threading.Thread.start') as mock_thread_start:
        websocket_manager.start()
        mock_thread_start.assert_called_once()


@pytest.mark.asyncio
async def test_connect(websocket_manager):
    websocket_manager.subscriptions = ["btcusdt@trade"]
    mock_websocket = AsyncMock()
    mock_websocket.__aenter__.return_value = mock_websocket
    mock_websocket.__aexit__.return_value = AsyncMock()

    async def mock_recv():
        await asyncio.sleep(0.1)
        websocket_manager.stop_event.set()
        return json.dumps(
            {'e': 'trade', 'E': 1622547600, 's': 'BTCUSDT', 't': 12345, 'p': '35000.0', 'q': '0.1', 'T': 1622547600,
             'm': True})

    mock_websocket.recv = mock_recv

    with patch('websockets.connect', return_value=mock_websocket):
        try:
            await asyncio.wait_for(websocket_manager.connect(), timeout=5)
        except asyncio.TimeoutError:
            pytest.fail("Timeout occurred")

        websocket_manager.stop()

    mock_websocket.send.assert_any_call(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": 1
    }))
    websocket_manager.socketio.emit.assert_called_once_with('market_data', {
        'e': 'trade', 'E': 1622547600, 's': 'BTCUSDT', 't': 12345, 'p': '35000.0', 'q': '0.1', 'T': 1622547600,
        'm': True
    })
