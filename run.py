from app import create_app, socketio
import threading
from app.consumer import main as start_consumer

app = create_app()

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

    socketio.run(app, debug=True)
