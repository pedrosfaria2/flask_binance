# Binance WebSocket Market Data

This project is a web application that uses WebSockets to receive real-time market data from Binance and detects price anomalies. The application is built with Flask on the backend and uses Socket.IO for real-time communication with the frontend.

## Features

- Connects to Binance WebSocket API to receive real-time market data.
- Detects price anomalies using a Z-Score algorithm.
- Publishes price anomaly alerts to a RabbitMQ queue.
- Web interface to view market data and alerts in real-time.

## Installation

### Prerequisites

- Python 3.8 or higher
- RabbitMQ
- Docker

### Steps to Install

1. Clone the repository:

    ```bash
    git clone https://github.com/pedrosfaria2/flask_binance.git
    cd flask_binance
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # For Linux/MacOS
    .\.venv\Scripts\activate  # For Windows
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start RabbitMQ using Docker:

    ```bash
    docker-compose up --build
    ```

2. Start the backend server:

    ```bash
    python run.py
    ```

3. Open your web browser and go to [http://localhost:5000](http://localhost:5000).

4. Click "Start WebSocket".

5. Subscribe to any symbols you are interested in.

6. Start the price anomaly worker:

    ```bash
    python -m price_anomaly_worker.run_worker
    ```
   
Note: The anomaly detection algorithm is configured with a 1-second interval so that alerts can be seen more frequently to experiment with the app. Feel free to adjust it as needed.

7. Enjoy the real-time market data and alerts!

## Tests

- The project includes a comprehensive suite of unit tests.
- To run the tests, simply execute:

    ```bash
    pytest
    ```