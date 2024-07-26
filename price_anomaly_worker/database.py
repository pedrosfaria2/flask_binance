import sqlite3
import os

# Defina o caminho relativo para o banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'market_data.db')


def get_symbols():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = "SELECT DISTINCT symbol FROM market_data"
        cursor.execute(query)
        symbols = cursor.fetchall()
        conn.close()
        return [symbol[0] for symbol in symbols]
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
        return []


def get_prices_for_symbol(symbol):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = f"SELECT price FROM market_data WHERE symbol = '{symbol}' ORDER BY event_time DESC LIMIT 100"
        cursor.execute(query)
        prices = cursor.fetchall()
        conn.close()
        return [float(price[0]) for price in prices]
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
        return []
