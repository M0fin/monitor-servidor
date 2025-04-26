import os
import time
import smtplib
from email.mime.text import MIMEText
import requests
import threading
from flask import Flask
from datetime import datetime

# Configuraciones
SERVER_URL = os.getenv('SERVER_URL')
CHECK_INTERVAL_NORMAL = int(os.getenv('CHECK_INTERVAL_NORMAL', '600'))  # 10 min
CHECK_INTERVAL_CAIDO = int(os.getenv('CHECK_INTERVAL_CAIDO', '30'))     # 30 seg

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

DESTINATARIOS = os.getenv('DESTINATARIO').split(',')

app = Flask(__name__)

@app.route('/')
def home():
    return "Monitor corriendo 🚀", 200

def iniciar_servidor_web():
    app.run(host="0.0.0.0", port=10000)

def log_evento(mensaje):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("monitor.log", "a") as log_file:
        log_file.write(f"[{now}] {mensaje}\n")

def enviar_correo(asunto, mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = SMTP_USER
    msg['To'] = ", ".join(DESTINATARIOS)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, DESTINATARIOS, msg.as_string())
        print(f"📤 Correo enviado: {mensaje}")
        log_evento(f"[ENVIADO] {asunto} → {mensaje}")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        log_evento(f"[ERROR] Al enviar correo → {e}")

def verificar_http():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def iniciar_monitoreo():
    caido = False
    intervalo = CHECK_INTERVAL_NORMAL
    print(f"🚀 Monitoreando: {SERVER_URL}...")

    while True:
        if verificar_http():
            if caido:
                enviar_correo("✅ Servidor Recuperado", f"El servidor de la intranet IM volvió en línea.")
                caido = False
                intervalo = CHECK_INTERVAL_NORMAL
            else:
                log_evento(f"[OK] Verificado: {SERVER_URL} está en línea.")
        else:
            if not caido:
                caido = True  # activa modo de caída
                print(f"⚠️ Servidor en caída detectada, iniciando alertas continuas...")
            enviar_correo("⚠️ Servidor Caído", "El servidor de la intranet IM no responde.")
            intervalo = CHECK_INTERVAL_CAIDO

        time.sleep(intervalo)

if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor_web, daemon=True).start()
    iniciar_monitoreo()
