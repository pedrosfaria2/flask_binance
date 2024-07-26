import time
import pika
import json
from .anomaly_detection import detect_anomalies
from .database import get_symbols, get_prices_for_symbol


class PriceAnomalyWorker:
    def __init__(self, rabbitmq_host='localhost', rabbitmq_port=5672, rabbitmq_user='user', rabbitmq_pass='password'):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_pass = rabbitmq_pass

        print(
            f"Attempting to connect to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port} with user {self.rabbitmq_user}")

        for _ in range(5):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
                ))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='price_anomalies')
                print("Connected to RabbitMQ")
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Error connecting to RabbitMQ: {e}")
                time.sleep(5)
        else:
            raise Exception("Could not connect to RabbitMQ after 5 retries")

    def publish_anomaly(self, symbol, current_price):
        alert = {
            'symbol': symbol,
            'current_price': current_price,
            'message': 'Price anomaly detected!'
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='price_anomalies',
            body=json.dumps(alert)
        )
        print(f'Published alert: {alert}')

    def run(self):
        while True:
            symbols = get_symbols()
            if not symbols:
                print("No symbols found or error accessing the database.")
                time.sleep(5)
                continue

            for symbol in symbols:
                prices = get_prices_for_symbol(symbol)
                if len(prices) < 30:
                    continue
                if detect_anomalies(prices):
                    self.publish_anomaly(symbol, float(prices[-1]))
            time.sleep(1)
