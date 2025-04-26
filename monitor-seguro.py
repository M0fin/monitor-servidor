import os
import time
import smtplib
from email.mime.text import MIMEText
import requests
import threading
from flask import Flask

# Configuraciones desde variables de entorno
SERVER_URL = os.getenv('SERVER_URL')
CHECK_INTERVAL = 30  # segundos

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
DESTINATARIO = os.getenv('DESTINATARIO')

# Configurar servidor Flask para abrir un puerto (así Render no apaga el servicio)
app = Flask(__name__)

@app.route('/')
def home():
    return "Monitor corriendo 🚀", 200

def iniciar_servidor_web():
    app.run(host="0.0.0.0", port=10000)

def enviar_sms(asunto, mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = SMTP_USER
    msg['To'] = DESTINATARIO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, DESTINATARIO, msg.as_string())
        print(f"📤 SMS enviado: {mensaje}")
    except Exception as e:
        print(f"❌ Error al enviar SMS: {e}")

def verificar_http():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def iniciar_monitoreo():
    caido = False
    print(f"🚀 Monitoreando: {SERVER_URL} cada {CHECK_INTERVAL} segundos...")

    while True:
        if verificar_http():
            if caido:
                enviar_sms("Servidor Recuperado", f"✅ {SERVER_URL} volvió en línea.")
                caido = False
        else:
            if not caido:
                enviar_sms("Servidor Caído", f"⚠️ {SERVER_URL} no responde.")
                caido = True
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor_web).start()
    iniciar_monitoreo()
