import os
import time
import smtplib
from email.mime.text import MIMEText
import requests

# Configuraciones
SERVER_URL = os.getenv('SERVER_URL')
CHECK_INTERVAL = 30  # segundos

# Configuración de correo SMTP desde variables de entorno
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
DESTINATARIO = os.getenv('DESTINATARIO')

def enviar_sms(asunto, mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = SMTP_USER
    msg['To'] = DESTINATARIO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, DESTINATARIO, msg.as_string())
    print(f"SMS enviado: {mensaje}")

def verificar_http():
    try:
        response = requests.get(SERVER_URL, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

caido = False

while True:
    if verificar_http():
        if caido:
            enviar_sms("Servidor Recuperado", f"✅ {SERVER_URL} volvió en línea.")
            caido = False
    else:
        if not caido:
            enviar_sms("Servidor Caído", f"⚠️ {SERVER_URL} está caído.")
            caido = True
    time.sleep(CHECK_INTERVAL)
