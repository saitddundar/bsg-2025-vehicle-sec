import socket
import json
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

EV_LOG = "logs/ev_log.txt"

MITM_HOST = "127.0.0.1"
MITM_PORT = 8000

EV_ID = "EV_42"
REAL_STATION_ID = "STATION_001"

def log(msg):
    with open(EV_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def start_ev():
    message = {
        "ev_id": EV_ID,
        "station_id": REAL_STATION_ID,
        "action": "START_CHARGING"
    }

    log(f"Şarj isteği gönderiliyor: {message}")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((MITM_HOST, MITM_PORT))
    client.send(json.dumps(message).encode())

    response = client.recv(4096).decode()
    client.close()

    log(f"CSMS yanıtı alındı: {response}")
    print("🚗 EV yanıt aldı:", response)

if __name__ == "__main__":
    start_ev()
