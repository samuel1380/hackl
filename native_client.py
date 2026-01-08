import cv2
import socketio
import base64
import time
import requests
import platform
import threading

# Configurações
SERVER_URL = "http://localhost:5000" # Mude para a URL do seu Render no deploy
LINK_CODE = "INSIRA_O_CODIGO_AQUI"

sio = socketio.Client(reconnection=True, reconnection_attempts=0)

def capture_and_send():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a câmera.")
        return

    print("Conectado ao servidor. Transmitindo...")
    
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                break

            # Redimensionar para economizar banda
            frame = cv2.resize(frame, (640, 480))
            
            # Codificar em JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            
            # Converter para Base64
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # Enviar via Socket.IO
            sio.emit('native_frame', {
                'id': sio.sid,
                'frame': 'data:image/jpeg;base64,' + jpg_as_text
            })
            
            # Controlar FPS (aprox 15 FPS)
            time.sleep(0.06)
            
        except Exception as e:
            print(f"Erro na captura: {e}")
            time.sleep(1)

    cap.release()

@sio.event
def connect():
    print("Conexão estabelecida com o servidor!")
    # Registrar o acesso no banco de dados via API
    try:
        requests.post(f"{SERVER_URL}/log_access", json={
            'code': LINK_CODE,
            'browser': 'Native Client',
            'os': platform.system() + " " + platform.release(),
            'email': 'native@client.app'
        })
    except:
        pass
    
    # Iniciar captura em thread separada
    thread = threading.Thread(target=capture_and_send)
    thread.daemon = True
    thread.start()

@sio.event
def disconnect():
    print("Desconectado do servidor.")

if __name__ == "__main__":
    print("--- Cliente de Monitoramento Nativo ---")
    print("Este aplicativo manterá a câmera ativa em segundo plano.")
    
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except Exception as e:
        print(f"Não foi possível conectar ao servidor: {e}")
