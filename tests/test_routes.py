import unittest
import json
from unittest.mock import patch
from app import create_app
from app.database import DatabaseManager


class MockWebSocketManager:
    def start(self):
        pass

    def stop(self):
        pass

    def subscribe(self, stream_name):
        pass

    def unsubscribe(self, stream_name):
        pass


@patch('app.routes.WebSocketManager', new=MockWebSocketManager)
class TestRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db = 'test_market_data.db'
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.db_manager = DatabaseManager(db_name=cls.test_db)

    @classmethod
    def tearDownClass(cls):
        import os
        os.remove(cls.test_db)

    def setUp(self):
        self.db_manager.create_tables()
        self.clear_database()

    def clear_database(self):
        with self.db_manager.connection:
            self.db_manager.connection.execute("DELETE FROM market_data")
            self.db_manager.connection.execute("DELETE FROM alerts")

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Binance Market Data', response.data)

    def test_start_route(self):
        response = self.client.get('/start')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)

    def test_stop_route(self):
        response = self.client.get('/stop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)

    def test_subscribe_route(self):
        response = self.client.get('/subscribe?symbol=BTCUSD')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'subscribed to BTCUSD@trade', response.data)

    def test_unsubscribe_route(self):
        response = self.client.get('/unsubscribe?symbol=BTCUSD')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'unsubscribed from BTCUSD@trade', response.data)

    def test_symbols_route(self):
        response = self.client.get('/symbols')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(json.loads(response.data), list)

    def test_alert_route(self):
        alert = {
            'symbol': 'BTCUSD',
            'current_price': 50000.0,
            'message': 'Price anomaly detected!'
        }
        response = self.client.post('/alert', json=alert)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alert received', response.data)


if __name__ == "__main__":
    unittest.main()
