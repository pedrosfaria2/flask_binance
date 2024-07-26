import pytest
from unittest.mock import patch, MagicMock, call
from price_anomaly_worker.worker import PriceAnomalyWorker


@pytest.fixture
def mock_rabbitmq_connection():
    with patch('pika.BlockingConnection') as mock_connection:
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel
        yield mock_conn, mock_channel


@pytest.fixture
def mock_get_symbols():
    with patch('price_anomaly_worker.worker.get_symbols') as mock:
        yield mock


@pytest.fixture
def mock_get_prices_for_symbol():
    with patch('price_anomaly_worker.worker.get_prices_for_symbol') as mock:
        yield mock


@pytest.fixture
def mock_detect_anomalies():
    with patch('price_anomaly_worker.worker.detect_anomalies') as mock:
        yield mock


def test_rabbitmq_connection_attempts(mock_rabbitmq_connection):
    mock_conn, mock_channel = mock_rabbitmq_connection

    PriceAnomalyWorker()

    assert mock_conn.channel.called
    mock_channel.queue_declare.assert_called_with(queue='price_anomalies')


def test_publish_anomaly(mock_rabbitmq_connection):
    mock_conn, mock_channel = mock_rabbitmq_connection
    worker = PriceAnomalyWorker()

    worker.publish_anomaly('BTCUSDT', 100.0)

    expected_call = call(
        exchange='',
        routing_key='price_anomalies',
        body='{"symbol": "BTCUSDT", "current_price": 100.0, "message": "Price anomaly detected!"}'
    )
    mock_channel.basic_publish.assert_has_calls([expected_call])


def test_run_with_anomalies(mock_rabbitmq_connection, mock_get_symbols, mock_get_prices_for_symbol,
                            mock_detect_anomalies):
    mock_conn, mock_channel = mock_rabbitmq_connection
    mock_get_symbols.return_value = ['BTCUSDT']
    mock_get_prices_for_symbol.return_value = [100] * 31
    mock_detect_anomalies.return_value = True

    worker = PriceAnomalyWorker()

    def stop_after_iterations(*args, **kwargs):
        worker.running = False
        raise Exception("Stop Iteration")

    with patch('time.sleep', side_effect=stop_after_iterations):
        with pytest.raises(Exception, match="Stop Iteration"):
            worker.run()

    mock_get_symbols.assert_called_once()
    mock_get_prices_for_symbol.assert_called_once_with('BTCUSDT')
    mock_channel.basic_publish.assert_called_once()
