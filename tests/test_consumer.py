import pytest
from unittest.mock import patch
from app.consumer import main, callback
import json


@pytest.fixture
def mock_socketio_emit(mocker):
    return mocker.patch('app.socketio.emit')


@pytest.fixture
def mock_pika_connection(mocker):
    mock_conn = mocker.Mock()
    mock_channel = mocker.Mock()
    mock_conn.channel.return_value = mock_channel
    mocker.patch('pika.BlockingConnection', return_value=mock_conn)
    return mock_conn, mock_channel


def test_callback(mock_socketio_emit):
    body = json.dumps({'symbol': 'BTCUSDT', 'current_price': 45000, 'message': 'Price anomaly detected!'})
    callback(None, None, None, body)
    mock_socketio_emit.assert_called_once_with('price_anomaly', json.loads(body))


def test_main(mock_pika_connection, mock_socketio_emit):
    mock_conn, mock_channel = mock_pika_connection
    with patch('time.sleep', return_value=None):
        main()
    mock_conn.channel.assert_called_once()
    mock_channel.queue_declare.assert_called_once_with(queue='price_anomalies')
    mock_channel.basic_consume.assert_called_once_with(queue='price_anomalies', on_message_callback=callback,
                                                       auto_ack=True)
    mock_channel.start_consuming.assert_called_once()
