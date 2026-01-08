"""
Script de migração do banco de dados
Adiciona novos campos aos models existentes
"""

from app import app, db
from models import Link, AccessLog
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_database():
    """Executa migração do banco de dados"""
    with app.app_context():
        logger.info("🔄 Iniciando migração do banco de dados...")
        
        try:
            # Verificar se as novas colunas já existem
            link_columns_to_add = {
                'max_uses': 'INTEGER DEFAULT 0',
                'current_uses': 'INTEGER DEFAULT 0',
                'notes': 'TEXT',
                'created_by': 'VARCHAR(100) DEFAULT "admin"',
                'last_accessed': 'DATETIME'
            }
            
            log_columns_to_add = {
                'user_agent': 'VARCHAR(255)',
                'country': 'VARCHAR(50)',
                'city': 'VARCHAR(100)',
                'session_duration': 'INTEGER DEFAULT 0'
            }
            
            # Adicionar colunas na tabela Link
            for column, column_type in link_columns_to_add.items():
                if not check_column_exists('link', column):
                    logger.info(f"➕ Adicionando coluna '{column}' na tabela 'link'...")
                    db.engine.execute(f'ALTER TABLE link ADD COLUMN {column} {column_type}')
                else:
                    logger.info(f"✅ Coluna '{column}' já existe na tabela 'link'")
            
            # Adicionar colunas na tabela AccessLog
            for column, column_type in log_columns_to_add.items():
                if not check_column_exists('access_log', column):
                    logger.info(f"➕ Adicionando coluna '{column}' na tabela 'access_log'...")
                    db.engine.execute(f'ALTER TABLE access_log ADD COLUMN {column} {column_type}')
                else:
                    logger.info(f"✅ Coluna '{column}' já existe na tabela 'access_log'")
            
            logger.info("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro durante migração: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_database()
