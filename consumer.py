import pika
import json
import time


def callback(ch, method, properties, body):
    alert = json.loads(body)
    print(f"Received alert: {alert}")


def main():
    print("Attempting to connect to RabbitMQ at localhost:5672 with user user")
    for _ in range(5):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=pika.PlainCredentials('user', 'password')
            ))
            channel = connection.channel()
            channel.queue_declare(queue='price_anomalies')
            print("Connected to RabbitMQ")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Could not connect to RabbitMQ: {e}")
            time.sleep(5)
    else:
        raise Exception("Could not connect to RabbitMQ after 5 retries")

    channel.basic_consume(queue='price_anomalies', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    main()
