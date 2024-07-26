import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from price_anomaly_worker.database import get_symbols, get_prices_for_symbol


@patch('price_anomaly_worker.database.DATABASE_PATH', ':memory:')
def test_get_symbols():
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [('BTCUSDT',), ('ETHUSDT',)]
        symbols = get_symbols()

        mock_connect.assert_called_once_with(':memory:')
        mock_cursor.execute.assert_called_once_with("SELECT DISTINCT symbol FROM market_data")
        assert symbols == ['BTCUSDT', 'ETHUSDT']


@patch('price_anomaly_worker.database.DATABASE_PATH', ':memory:')
def test_get_symbols_db_error():
    with patch('sqlite3.connect', side_effect=sqlite3.Error("Database error")) as mock_connect:
        symbols = get_symbols()

        mock_connect.assert_called_once_with(':memory:')
        assert symbols == []


@patch('price_anomaly_worker.database.DATABASE_PATH', ':memory:')
def test_get_prices_for_symbol():
    with patch('sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [(100.0,), (101.0,)]
        prices = get_prices_for_symbol('BTCUSDT')

        mock_connect.assert_called_once_with(':memory:')
        mock_cursor.execute.assert_called_once_with(
            "SELECT price FROM market_data WHERE symbol = 'BTCUSDT' ORDER BY event_time DESC LIMIT 100")
        assert prices == [100.0, 101.0]


@patch('price_anomaly_worker.database.DATABASE_PATH', ':memory:')
def test_get_prices_for_symbol_db_error():
    with patch('sqlite3.connect', side_effect=sqlite3.Error("Database error")) as mock_connect:
        prices = get_prices_for_symbol('BTCUSDT')

        mock_connect.assert_called_once_with(':memory:')
        assert prices == []
