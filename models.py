from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

class Link(db.Model):
    """Modelo para links de acesso temporários"""
    
    __tablename__ = 'link'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Novos campos
    max_uses = db.Column(db.Integer, default=0)  # 0 = ilimitado
    current_uses = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), default='admin')
    last_accessed = db.Column(db.DateTime, nullable=True)

    def is_expired(self):
        """Verifica se o link expirou por tempo"""
        return datetime.utcnow() > self.expires_at

    def is_usage_exceeded(self):
        """Verifica se o link excedeu o número máximo de usos"""
        if self.max_uses == 0:  # Ilimitado
            return False
        return self.current_uses >= self.max_uses

    def can_be_used(self):
        """Verifica se o link pode ser usado (ativo, não expirado, não excedeu usos)"""
        return (
            self.is_active and 
            not self.is_expired() and 
            not self.is_usage_exceeded()
        )

    def increment_usage(self):
        """Incrementa o contador de usos e atualiza último acesso"""
        self.current_uses += 1
        self.last_accessed = datetime.utcnow()

    def deactivate(self):
        """Desativa o link manualmente"""
        self.is_active = False

    def get_remaining_uses(self):
        """Retorna quantos usos restam (None se ilimitado)"""
        if self.max_uses == 0:
            return None
        return max(0, self.max_uses - self.current_uses)

    def get_time_remaining(self):
        """Retorna tempo restante até expiração"""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - datetime.utcnow()

    def to_dict(self):
        """Converte para dicionário (útil para API)"""
        return {
            'id': self.id,
            'code': self.code,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'remaining_uses': self.get_remaining_uses(),
            'notes': self.notes,
            'created_by': self.created_by,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'total_logs': len(self.logs)
        }

    def __repr__(self):
        return f'<Link {self.code[:8]}... (expires: {self.expires_at})>'


class AccessLog(db.Model):
    """Modelo para logs de acesso aos links"""
    
    __tablename__ = 'access_log'
    
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    email = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Novos campos
    user_agent = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    session_duration = db.Column(db.Integer, default=0)  # em segundos

    link = db.relationship('Link', backref=db.backref('logs', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        """Converte para dicionário (útil para API)"""
        return {
            'id': self.id,
            'link_code': self.link.code if self.link else None,
            'ip_address': self.ip_address,
            'browser': self.browser,
            'os': self.os,
            'email': self.email,
            'timestamp': self.timestamp.isoformat(),
            'user_agent': self.user_agent,
            'country': self.country,
            'city': self.city,
            'session_duration': self.session_duration
        }

    def __repr__(self):
        return f'<AccessLog {self.id} - {self.ip_address} at {self.timestamp}>'
