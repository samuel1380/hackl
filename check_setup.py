"""
Script de verificação de configuração do sistema
Executa checagens para garantir que tudo está configurado corretamente
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NÃO ENCONTRADO: {filepath}")
        return False

def check_env_variable(var_name, required=True):
    """Verifica se uma variável de ambiente está definida"""
    value = os.getenv(var_name)
    if value:
        # Não mostrar valor de SECRET_KEY por segurança
        if var_name == 'SECRET_KEY':
            print(f"✅ {var_name}: {'*' * 20} (definida)")
        else:
            print(f"✅ {var_name}: {value}")
        return True
    else:
        if required:
            print(f"❌ {var_name}: NÃO DEFINIDA")
        else:
            print(f"⚠️  {var_name}: Não definida (opcional)")
        return not required

def check_secret_key():
    """Verifica se SECRET_KEY foi alterada do padrão"""
    from dotenv import load_dotenv
    load_dotenv()
    
    secret = os.getenv('SECRET_KEY', '')
    default_keys = [
        'secret_key_123',
        'dev_key_change_in_production',
        'd8f3a9b2c1e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0'
    ]
    
    if secret.lower() in [k.lower() for k in default_keys]:
        print(f"⚠️  SECRET_KEY ainda está com valor padrão! ALTERE IMEDIATAMENTE!")
        return False
    else:
        print(f"✅ SECRET_KEY foi alterada (segura)")
        return True

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask_socketio',
        'flask_sqlalchemy',
        'flask_limiter',
        'dotenv',
        'cv2',
        'socketio',
        'mss',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} NÃO INSTALADO")
            missing.append(package)
    
    return len(missing) == 0

def main():
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE CONFIGURAÇÃO DO SISTEMA")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. Verificar arquivos essenciais
    print("📁 VERIFICANDO ARQUIVOS ESSENCIAIS...")
    files_ok = all([
        check_file_exists('.env', 'Arquivo de ambiente'),
        check_file_exists('.env.example', 'Template de ambiente'),
        check_file_exists('config.py', 'Arquivo de configuração'),
        check_file_exists('app.py', 'Servidor principal'),
        check_file_exists('models.py', 'Modelos do banco'),
        check_file_exists('requirements.txt', 'Dependências'),
        check_file_exists('README.md', 'Documentação'),
    ])
    print()
    
    # 2. Verificar variáveis de ambiente
    print("⚙️  VERIFICANDO VARIÁVEIS DE AMBIENTE...")
    from dotenv import load_dotenv
    load_dotenv()
    
    env_ok = all([
        check_env_variable('SECRET_KEY', required=True),
        check_env_variable('DATABASE_URL', required=True),
        check_env_variable('SERVER_URL', required=True),
        check_env_variable('PORT', required=False),
        check_env_variable('MAX_LINK_EXPIRY_MINUTES', required=False),
    ])
    print()
    
    # 3. Verificar SECRET_KEY
    print("🔐 VERIFICANDO SEGURANÇA...")
    secret_ok = check_secret_key()
    print()
    
    # 4. Verificar dependências
    print("📦 VERIFICANDO DEPENDÊNCIAS PYTHON...")
    deps_ok = check_dependencies()
    print()
    
    # 5. Verificar permissões de escrita
    print("📝 VERIFICANDO PERMISSÕES...")
    try:
        test_file = 'test_write.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Permissão de escrita: OK")
        write_ok = True
    except Exception as e:
        print(f"❌ Permissão de escrita: FALHOU ({e})")
        write_ok = False
    print()
    
    # Resultado final
    print("=" * 60)
    all_ok = files_ok and env_ok and secret_ok and deps_ok and write_ok
    
    if all_ok:
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("🚀 Sistema pronto para uso!")
        print()
        print("Para iniciar o servidor:")
        print("  python app.py")
        return 0
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM!")
        print()
        print("Ações necessárias:")
        if not files_ok:
            print("  - Verifique se todos os arquivos foram criados")
        if not env_ok:
            print("  - Configure as variáveis no arquivo .env")
        if not secret_ok:
            print("  - Altere a SECRET_KEY no arquivo .env")
            print("    Execute: python -c \"import secrets; print(secrets.token_hex(32))\"")
        if not deps_ok:
            print("  - Instale as dependências: pip install -r requirements.txt")
        if not write_ok:
            print("  - Verifique as permissões do diretório")
        return 1
    
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
