import sqlite3


class DatabaseManager:
    def __init__(self, db_name='market_data.db'):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    event_type TEXT,
                    event_time INTEGER,
                    symbol TEXT,
                    trade_id INTEGER,
                    price TEXT,
                    quantity TEXT,
                    trade_time INTEGER,
                    is_buyer_market_maker INTEGER
                )
            ''')

    def insert_data(self, data):
        with self.connection:
            self.connection.execute('''
                INSERT INTO market_data (
                    event_type, event_time, symbol, trade_id, price, quantity, trade_time, is_buyer_market_maker
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['e'], data['E'], data['s'], data['t'], data['p'], data['q'], data['T'], data['m']))
