import os
import pytest
import sqlite3
from app.database import DatabaseManager

TEST_DB = 'test_market_data.db'


@pytest.fixture
def db():
    db = DatabaseManager(TEST_DB)
    yield db
    os.remove(TEST_DB)


def test_create_tables(db):

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_data';")
    market_data_table = cursor.fetchone()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts';")
    alerts_table = cursor.fetchone()
    conn.close()

    assert market_data_table is not None
    assert alerts_table is not None


def test_insert_data(db):
    data = {
        'e': 'trade',
        'E': 1622547600,
        's': 'BTCUSDT',
        't': 12345,
        'p': '35000.0',
        'q': '0.1',
        'T': 1622547600,
        'm': 1
    }
    db.insert_data(data)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market_data WHERE trade_id = 12345;")
    inserted_data = cursor.fetchone()
    conn.close()

    assert inserted_data is not None
    assert inserted_data[0] == 'trade'
    assert inserted_data[1] == 1622547600
    assert inserted_data[2] == 'BTCUSDT'
    assert inserted_data[3] == 12345
    assert inserted_data[4] == '35000.0'
    assert inserted_data[5] == '0.1'
    assert inserted_data[6] == 1622547600
    assert inserted_data[7] == 1


def test_insert_alert(db):
    alert = {
        'symbol': 'BTCUSDT',
        'current_price': 35000.0,
        'message': 'Price anomaly detected!'
    }
    db.insert_alert(alert)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE symbol = 'BTCUSDT';")
    inserted_alert = cursor.fetchone()
    conn.close()

    assert inserted_alert is not None
    assert inserted_alert[1] == 'BTCUSDT'
    assert inserted_alert[2] == 35000.0
    assert inserted_alert[3] == 'Price anomaly detected!'
