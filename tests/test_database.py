import unittest
from app.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_name = 'test_market_data.db'
        self.db_manager = DatabaseManager(db_name=self.db_name)
        self.db_manager.create_tables()

    def tearDown(self):
        self.db_manager.connection.close()
        import os
        os.remove(self.db_name)

    def test_create_table(self):
        query = '''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('market_data', 'alerts')
        '''
        cursor = self.db_manager.connection.execute(query)
        tables = cursor.fetchall()
        self.assertEqual(len(tables), 2)

    def test_insert_data(self):
        data = {
            'e': 'trade',
            'E': 123456789,
            's': 'BTCUSD',
            't': 12345,
            'p': '50000.0',
            'q': '0.1',
            'T': 123456789,
            'm': 1
        }
        self.db_manager.insert_data(data)
        query = 'SELECT * FROM market_data WHERE symbol = ?'
        cursor = self.db_manager.connection.execute(query, (data['s'],))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[2], data['s'])


if __name__ == "__main__":
    unittest.main()
