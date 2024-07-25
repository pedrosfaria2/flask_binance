import asyncio
import websockets
import threading
import json
from .database import DatabaseManager


class WebSocketManager:
    def __init__(self, socketio):
        self.uri = "wss://stream.binance.com:9443/ws"
        self.connection = None
        self.loop = None
        self.thread = None
        self.socketio = socketio
        self.subscriptions = []
        self.db_manager = DatabaseManager()
        self.stop_event = threading.Event()

    def start(self):
        self.stop_event.clear()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_loop, args=(self.loop,))
        self.thread.start()

    async def stop_task(self):
        await self.connection.close()
        self.loop.stop()

    def run_loop(self, loop):
        asyncio.set_event_loop(loop)
        connect_task = loop.create_task(self.connect())
        loop.run_until_complete(connect_task)

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
        try:
            while not self.stop_event.is_set():
                message = await self.connection.recv()
                data = json.loads(message)
                if 'e' in data and data['e'] == 'trade':
                    self.socketio.emit('market_data', data)
                    self.db_manager.insert_data(data)
        except websockets.ConnectionClosed:
            pass
        except asyncio.CancelledError:
            pass
        finally:
            if self.connection:
                await self.connection.close()

    def stop(self):
        self.stop_event.set()
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.stop_task(), self.loop)
        if self.thread:
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
