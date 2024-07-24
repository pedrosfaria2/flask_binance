import asyncio
import websockets
import threading
import json

class WebSocketManager:
    def __init__(self, socketio):
        self.uri = "wss://stream.binance.com:9443/ws"
        self.connection = None
        self.loop = None
        self.thread = None
        self.socketio = socketio
        self.subscriptions = []

    def start(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_loop, args=(self.loop,))
        self.thread.start()

    def run_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    async def connect(self):
        async with websockets.connect(self.uri, ping_interval=180, ping_timeout=600) as websocket:
            self.connection = websocket
            await self.manage_subscriptions()
            await self.receive_messages()

    async def manage_subscriptions(self):
        for symbol in self.subscriptions:
            await self.connection.send(json.dumps({
                "method": "SUBSCRIBE",
                "params": [symbol],
                "id": 1
            }))

    async def receive_messages(self):
        while True:
            try:
                message = await self.connection.recv()
                data = json.loads(message)
                if 'e' in data and data['e'] == 'trade':
                    self.socketio.emit('market_data', data)
            except websockets.ConnectionClosed:
                break

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

    def subscribe(self, stream_name):
        if stream_name not in self.subscriptions:
            self.subscriptions.append(stream_name)
            if self.connection:
                message = {
                    "method": "SUBSCRIBE",
                    "params": [stream_name],
                    "id": 1
                }
                asyncio.run_coroutine_threadsafe(self.connection.send(json.dumps(message)), self.loop)

    def unsubscribe(self, stream_name):
        if stream_name in self.subscriptions:
            self.subscriptions.remove(stream_name)
            if self.connection:
                message = {
                    "method": "UNSUBSCRIBE",
                    "params": [stream_name],
                    "id": 2
                }
                asyncio.run_coroutine_threadsafe(self.connection.send(json.dumps(message)), self.loop)
