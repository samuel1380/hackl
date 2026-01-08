from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    email = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    link = db.relationship('Link', backref=db.backref('logs', lazy=True))
