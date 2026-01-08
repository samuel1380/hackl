import os
import subprocess
import sys

def build():
    print("--- Iniciando Build do Executável ---")
    
    # Verificar se pyinstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Comando do PyInstaller
    # --onefile: cria um único executável
    # --noconsole: não abre janela de terminal (prompt)
    # --name: nome do arquivo final
    # --hidden-import: garante que bibliotecas dinâmicas sejam incluídas
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=MonitoramentoSeguro",
        "--hidden-import=cv2",
        "--hidden-import=socketio",
        "--hidden-import=engineio.async_drivers.threading",
        "monitor_cliente.py"
    ]

    print(f"Executando: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\n--- Build Concluído com Sucesso! ---")
    print("O arquivo executável está na pasta: dist/MonitoramentoSeguro.exe")

if __name__ == "__main__":
    build()
