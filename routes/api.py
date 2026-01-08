"""
Blueprint para rotas da API REST
Versão: v1
"""

from flask import Blueprint, request, jsonify
from models import db, Link, AccessLog
from config import Config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Criar Blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/links', methods=['GET'])
def get_links():
    """Lista todos os links"""
    try:
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtros
        active_only = request.args.get('active', 'false').lower() == 'true'
        
        query = Link.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Ordenar por mais recente
        query = query.order_by(Link.created_at.desc())
        
        # Paginar
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'links': [link.to_dict() for link in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar links: {str(e)}")
        return jsonify({'error': 'Erro ao listar links'}), 500


@api.route('/links/<code>', methods=['GET'])
def get_link(code):
    """Obtém detalhes de um link específico"""
    try:
        link = Link.query.filter_by(code=code).first()
        
        if not link:
            return jsonify({'error': 'Link não encontrado'}), 404
        
        return jsonify(link.to_dict())
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter link {code}: {str(e)}")
        return jsonify({'error': 'Erro ao obter link'}), 500


@api.route('/links/<code>', methods=['DELETE'])
def delete_link(code):
    """Desativa um link"""
    try:
        link = Link.query.filter_by(code=code).first()
        
        if not link:
            return jsonify({'error': 'Link não encontrado'}), 404
        
        link.deactivate()
        db.session.commit()
        
        logger.info(f"🗑️  Link desativado: {code}")
        return jsonify({'message': 'Link desativado com sucesso'})
        
    except Exception as e:
        logger.error(f"❌ Erro ao desativar link {code}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao desativar link'}), 500


@api.route('/links/<code>', methods=['PATCH'])
def update_link(code):
    """Atualiza um link (notes, max_uses, etc)"""
    try:
        link = Link.query.filter_by(code=code).first()
        
        if not link:
            return jsonify({'error': 'Link não encontrado'}), 404
        
        data = request.json
        
        # Atualizar campos permitidos
        if 'notes' in data:
            link.notes = data['notes'][:500]
        
        if 'max_uses' in data:
            max_uses = int(data['max_uses'])
            if max_uses < 0:
                return jsonify({'error': 'max_uses não pode ser negativo'}), 400
            link.max_uses = max_uses
        
        if 'is_active' in data:
            link.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        logger.info(f"✏️  Link atualizado: {code}")
        return jsonify(link.to_dict())
        
    except ValueError:
        return jsonify({'error': 'Valores inválidos'}), 400
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar link {code}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar link'}), 500


@api.route('/logs', methods=['GET'])
def get_logs():
    """Lista logs de acesso"""
    try:
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtros
        link_code = request.args.get('link_code')
        ip_address = request.args.get('ip')
        
        query = AccessLog.query
        
        if link_code:
            link = Link.query.filter_by(code=link_code).first()
            if link:
                query = query.filter_by(link_id=link.id)
        
        if ip_address:
            query = query.filter_by(ip_address=ip_address)
        
        # Ordenar por mais recente
        query = query.order_by(AccessLog.timestamp.desc())
        
        # Paginar
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar logs: {str(e)}")
        return jsonify({'error': 'Erro ao listar logs'}), 500


@api.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas gerais"""
    try:
        total_links = Link.query.count()
        active_links = Link.query.filter_by(is_active=True).count()
        total_logs = AccessLog.query.count()
        
        # Links criados hoje
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        links_today = Link.query.filter(Link.created_at >= today).count()
        
        # Acessos hoje
        logs_today = AccessLog.query.filter(AccessLog.timestamp >= today).count()
        
        return jsonify({
            'total_links': total_links,
            'active_links': active_links,
            'total_logs': total_logs,
            'links_created_today': links_today,
            'accesses_today': logs_today
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro ao obter estatísticas'}), 500


@api.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
