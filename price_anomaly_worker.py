import sqlite3
import time
import numpy as np
from scipy.stats import zscore
import requests


class PriceAnomalyWorker:
    def __init__(self, db_name='market_data.db', server_url='http://localhost:5000'):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.server_url = server_url
        self.create_alerts_table()

    def create_alerts_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                current_price REAL NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def fetch_recent_data(self, symbol, window_size=100):
        query = '''
            SELECT price FROM market_data
            WHERE symbol = ?
            ORDER BY event_time DESC
            LIMIT ?
        '''
        cursor = self.connection.execute(query, (symbol, window_size))
        prices = cursor.fetchall()
        return [float(price[0]) for price in prices]

    def detect_anomalies(self, prices, threshold=3.0):
        z_scores = zscore(prices)
        anomalies = np.where(np.abs(z_scores) > threshold)
        return anomalies[0].size > 0

    def run(self):
        while True:
            symbols = self.get_symbols()
            for symbol in symbols:
                prices = self.fetch_recent_data(symbol)
                if len(prices) < 30:
                    continue
                if self.detect_anomalies(prices):
                    self.generate_alert(symbol, prices[-1])
            time.sleep(1)

    def get_symbols(self):
        query = 'SELECT DISTINCT symbol FROM market_data'
        cursor = self.connection.execute(query)
        symbols = cursor.fetchall()
        return [symbol[0] for symbol in symbols]

    def generate_alert(self, symbol, current_price):
        alert = {
            'symbol': symbol,
            'current_price': current_price,
            'message': 'Price anomaly detected!'
        }

        self.save_alert_to_db(alert)
        print(alert)

        try:
            response = requests.post(f'{self.server_url}/alert', json=alert)
            if response.status_code == 200:
                print(f'Alert sent: {alert}')
            else:
                print(f'Failed to send alert: {response.status_code}')
        except Exception as e:
            print(f'Error sending alert: {e}')

    def save_alert_to_db(self, alert):
        query = '''
            INSERT INTO alerts (symbol, current_price, message)
            VALUES (?, ?, ?)
        '''
        self.connection.execute(query, (alert['symbol'], alert['current_price'], alert['message']))
        self.connection.commit()


if __name__ == "__main__":
    worker = PriceAnomalyWorker()
    worker.run()
