import socket
import json

HOST = "127.0.0.1"
PORT = 9000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("[CSMS] Sunucu aktif, veri bekleniyor...")

while True:
    client, _ = server.accept()
    data = json.loads(client.recv(4096).decode())

    real_soc = data["real_soc"]
    reported_soc = data["reported_soc"]

    print(f"[CSMS] Gerçek SoC: %{real_soc} | Raporlanan SoC: %{reported_soc}")

    if reported_soc - real_soc >= 20:
        print("🚨 PHANTOM SOC (KAPASİTE SAHTEKÂRLIĞI) TESPİT EDİLDİ 🚨")
        print("➡️ Şarj oturumu durduruldu")
    else:
        print("✅ SoC değerleri tutarlı")

    client.close()
