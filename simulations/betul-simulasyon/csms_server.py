import socket
import json
import os
from datetime import datetime

# --- LOG KLASÖRÜ ---
os.makedirs("logs", exist_ok=True)

CSMS_LOG = "logs/csms_log.txt"
ALERT_LOG = "logs/alerts_log.txt"

HOST = "127.0.0.1"
PORT = 9000

# Sistemde kayıtlı (güvenilen) istasyonlar
KNOWN_STATIONS = ["STATION_001"]

def log(message):
    with open(CSMS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def alert(station_id, ev_id):
    with open("logs/alerts_log.txt", "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("🚨🚨🚨 ANOMALİ TESPİT EDİLDİ 🚨🚨🚨\n")
        f.write(f"Tarih/Saat        : {datetime.now()}\n")
        f.write("Anomali Türü      : Şarj İstasyonu Kimlik Sahteciliği (Identity Spoofing)\n")
        f.write(f"EV Kimliği        : {ev_id}\n")
        f.write(f"Gelen İstasyon ID : {station_id}\n")
        f.write("Beklenen Durum    : Kayıtlı / Güvenilir istasyon\n")
        f.write("Gerçek Durum      : Bilinmeyen / Yetkisiz istasyon\n")
        f.write("Güvenlik Kararı   : Oturum REDDEDİLDİ\n")
        f.write("Olası Etki        : Yetkisiz enerji aktarımı, faturalandırma manipülasyonu\n")
        f.write("Aksiyon           : Oturum sonlandırıldı ve loglandı\n")
        f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


def start_csms():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print("🟢 CSMS SERVER ÇALIŞIYOR...")
    log("CSMS server başlatıldı")

    while True:
        client, addr = server.accept()
        data = client.recv(4096).decode()
        message = json.loads(data)

        station_id = message.get("station_id")
        ev_id = message.get("ev_id")

        log(f"Gelen oturum isteği | EV: {ev_id} | İstasyon: {station_id}")

        if station_id not in KNOWN_STATIONS:
            alert(station_id, ev_id)
            response = {"status": "REJECTED", "reason": "Unknown station"}
        else:
            response = {"status": "ACCEPTED"}

        client.send(json.dumps(response).encode())
        client.close()

if __name__ == "__main__":
    start_csms()
