from flask import Blueprint, render_template, jsonify, request
from .websocket_manager import WebSocketManager
from .binance_api import fetch_symbols
from . import socketio

main = Blueprint('main', __name__)
ws_manager = WebSocketManager(socketio)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/start')
def start():
    ws_manager.start()
    return jsonify({"status": "started"})


@main.route('/stop')
def stop():
    ws_manager.stop()
    return jsonify({"status": "stopped"})


@main.route('/subscribe')
def subscribe():
    symbol = request.args.get('symbol')
    if symbol:
        ws_manager.subscribe(f"{symbol}@trade")
        return jsonify({"status": f"subscribed to {symbol}@trade"})
    return jsonify({"status": "symbol not provided"}), 400


@main.route('/unsubscribe')
def unsubscribe():
    symbol = request.args.get('symbol')
    if symbol:
        ws_manager.unsubscribe(f"{symbol}@trade")
        return jsonify({"status": f"unsubscribed from {symbol}@trade"})
    return jsonify({"status": "symbol not provided"}), 400


@main.route('/symbols')
async def symbols():
    symbols = await fetch_symbols()
    return jsonify(symbols)


@main.route('/alert', methods=['POST'])
def alert():
    alert_data = request.json
    socketio.emit('price_anomaly', alert_data)
    return jsonify({"status": "alert received"})
