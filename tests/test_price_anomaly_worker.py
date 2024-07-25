import unittest
from unittest.mock import patch, MagicMock

from price_anomaly_worker import PriceAnomalyWorker


class TestPriceAnomalyWorker(unittest.TestCase):
    @patch('app.price_anomaly_worker.sqlite3.connect')
    @patch('app.price_anomaly_worker.requests.post')
    def setUp(self, mock_requests_post, mock_sqlite_connect):
        self.mock_connection = MagicMock()
        mock_sqlite_connect.return_value = self.mock_connection
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.worker = PriceAnomalyWorker(db_name='test.db')
        self.mock_requests_post = mock_requests_post

    def test_create_alerts_table(self):
        self.worker.create_alerts_table()
        self.mock_connection.execute.assert_called_once()

    def test_fetch_recent_data(self):
        self.mock_cursor.fetchall.return_value = [(10,), (12,), (14,)]
        prices = self.worker.fetch_recent_data('BTCUSD', 100)
        self.assertEqual(prices, [10.0, 12.0, 14.0])

    def test_detect_anomalies(self):
        prices = [10.0, 12.0, 14.0, 1000.0]
        self.assertTrue(self.worker.detect_anomalies(prices))

    def test_get_symbols(self):
        self.mock_cursor.fetchall.return_value = [('BTCUSD',), ('ETHUSD',)]
        symbols = self.worker.get_symbols()
        self.assertEqual(symbols, ['BTCUSD', 'ETHUSD'])

    def test_generate_alert(self):
        with patch.object(self.worker, 'save_alert_to_db') as mock_save_alert_to_db:
            self.worker.generate_alert('BTCUSD', 1000.0)
            alert = {
                'symbol': 'BTCUSD',
                'current_price': 1000.0,
                'message': 'Price anomaly detected!'
            }
            mock_save_alert_to_db.assert_called_once_with(alert)
            self.mock_requests_post.assert_called_once_with('http://localhost:5000/alert', json=alert)

    def test_save_alert_to_db(self):
        alert = {
            'symbol': 'BTCUSD',
            'current_price': 1000.0,
            'message': 'Price anomaly detected!'
        }
        self.worker.save_alert_to_db(alert)
        self.mock_connection.execute.assert_called_once_with(
            'INSERT INTO alerts (symbol, current_price, message) VALUES (?, ?, ?)',
            ('BTCUSD', 1000.0, 'Price anomaly detected!')
        )
        self.mock_connection.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
