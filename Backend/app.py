import threading
import queue
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for demo

# Message queue (simulates Azure Service Bus)
message_queue = queue.Queue()

# Background worker thread
def message_processor():
    """Simulates a background service that processes messages from the queue."""
    while True:
        try:
            # Wait for a message (blocks until one is available)
            data = message_queue.get(timeout=1)
        except queue.Empty:
            continue

        # Simulate processing time (e.g., order validation, payment, etc.)
        print(f"Processing message: {data}")
        time.sleep(5)  # Simulate work

        # After processing, emit an event to all clients (or a specific room)
        # In a real app you might target a specific user; here we broadcast.
        socketio.emit('message_processed', {
            'id': data['id'],
            'content': data['content'],
            'status': 'processed',
            'result': 'Order confirmed!'
        })
        print(f"Finished processing: {data}")

# Start the background worker thread when the server starts
threading.Thread(target=message_processor, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')  # We'll create this HTML file

@socketio.on('send_message')
def handle_send_message(data):
    """Receives a message from the client and puts it into the queue."""
    # Attach a unique ID (simple timestamp) to track the message
    message_id = str(time.time())
    message_data = {
        'id': message_id,
        'content': data['message'],
        'status': 'pending'
    }
    # Put the message into the queue
    message_queue.put(message_data)
    # Immediately tell the client that the message is queued
    emit('message_queued', message_data)

if __name__ == '__main__':
    socketio.run(app, debug=True)