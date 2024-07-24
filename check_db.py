# check_db.py
from models import SessionLocal, Trade

def check_data():
    db = SessionLocal()
    trades = db.query(Trade).all()
    for trade in trades:
        print(f"ID: {trade.id}, Symbol: {trade.symbol}, Price: {trade.price}, Quantity: {trade.quantity}, Time: {trade.trade_time}")
    db.close()

if __name__ == "__main__":
    check_data()
