import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    """Configuração centralizada da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_change_in_production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server
    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
    PORT = int(os.getenv('PORT', 5000))
    
    # Security
    MAX_LINK_EXPIRY_MINUTES = int(os.getenv('MAX_LINK_EXPIRY_MINUTES', 1440))
    RATE_LIMIT_LINKS = os.getenv('RATE_LIMIT_LINKS', '5 per minute')
    RATE_LIMIT_ACCESS = os.getenv('RATE_LIMIT_ACCESS', '10 per minute')
    
    # Streaming
    CAMERA_FPS = int(os.getenv('CAMERA_FPS', 6))
    SCREEN_FPS = int(os.getenv('SCREEN_FPS', 2))
    JPEG_QUALITY_CAMERA = int(os.getenv('JPEG_QUALITY_CAMERA', 25))
    JPEG_QUALITY_SCREEN = int(os.getenv('JPEG_QUALITY_SCREEN', 20))
    
    # SocketIO
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '*')
    
    @staticmethod
    def validate():
        """Valida se as configurações críticas estão definidas"""
        if Config.SECRET_KEY == 'dev_key_change_in_production':
            print("⚠️  AVISO: SECRET_KEY padrão detectada! Altere no arquivo .env")
        
        if Config.MAX_LINK_EXPIRY_MINUTES > 10080:  # 7 dias
            raise ValueError("MAX_LINK_EXPIRY_MINUTES não pode exceder 7 dias (10080 minutos)")
        
        return True
