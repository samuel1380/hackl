"""
Blueprint para rotas do Dashboard (interface web)
"""

from flask import Blueprint, render_template, request, jsonify
from models import db, Link, AccessLog
from config import Config
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Criar Blueprint
dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def index():
    """Página principal do dashboard"""
    try:
        # Filtros opcionais
        filter_date = request.args.get('date')
        filter_ip = request.args.get('ip')
        filter_email = request.args.get('email')
        
        # Query de links
        links = Link.query.order_by(Link.created_at.desc()).all()
        
        # Query de logs com filtros
        logs_query = AccessLog.query
        
        if filter_date:
            try:
                date_obj = datetime.strptime(filter_date, '%Y-%m-%d')
                next_day = date_obj + timedelta(days=1)
                logs_query = logs_query.filter(
                    AccessLog.timestamp >= date_obj,
                    AccessLog.timestamp < next_day
                )
            except ValueError:
                pass
        
        if filter_ip:
            logs_query = logs_query.filter(AccessLog.ip_address.like(f'%{filter_ip}%'))
        
        if filter_email:
            logs_query = logs_query.filter(AccessLog.email.like(f'%{filter_email}%'))
        
        logs = logs_query.order_by(AccessLog.timestamp.desc()).limit(100).all()
        
        return render_template('dashboard.html', links=links, logs=logs)
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dashboard: {str(e)}")
        return "Erro ao carregar dashboard", 500


@dashboard.route('/generate_link', methods=['POST'])
def generate_link_route():
    """Rota para gerar links (será movida para cá do app.py)"""
    # Esta função será implementada quando movermos do app.py
    pass


@dashboard.route('/v/<code>')
def view_link_route(code):
    """Rota para visualizar link (será movida para cá do app.py)"""
    # Esta função será implementada quando movermos do app.py
    pass


@dashboard.route('/log_access', methods=['POST'])
def log_access_route():
    """Rota para registrar acesso (será movida para cá do app.py)"""
    # Esta função será implementada quando movermos do app.py
    pass
