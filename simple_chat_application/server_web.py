from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected users (username -> session ID)
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('set_username')
def handle_set_username(username):
    users[username] = request.sid
    print(f"[+] {username} joined (SID={request.sid})")
    emit('message', f"✅ {username} joined the chat!", broadcast=True)
    emit('user_list', list(users.keys()), broadcast=True)

@socketio.on('message')
def handle_message(msg):
    # Private message format: /pm <username> <message>
    if msg.startswith("/pm "):
        try:
            _, target_user, private_msg = msg.split(" ", 2)
            if target_user in users:
                target_sid = users[target_user]
                sender_name = [name for name, sid in users.items() if sid == request.sid][0]
                emit('message', f"(Private) You → {target_user}: {private_msg}", to=request.sid)
                emit('message', f"(Private) {sender_name} → You: {private_msg}", to=target_sid)
            else:
                emit('message', f"⚠️ User '{target_user}' not found.", to=request.sid)
        except ValueError:
            emit('message', "⚠️ Usage: /pm username message", to=request.sid)
    else:
        print(f"[Broadcast] {msg}")
        send(msg, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    disconnected_user = None
    for name, sid in list(users.items()):
        if sid == request.sid:
            disconnected_user = name
            del users[name]
            break
    if disconnected_user:
        print(f"[-] {disconnected_user} left")
        emit('message', f"❌ {disconnected_user} left the chat.", broadcast=True)
        emit('user_list', list(users.keys()), broadcast=True)

if __name__ == '__main__':
    print("🚀 Web Chat Server running at http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
