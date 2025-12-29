import socket
import json

HOST = "127.0.0.1"
PORT = 8000

message = {
    "ev_id": "EV_42",
    "real_soc": 60,
    "reported_soc": 60
}

print("[EV] Gerçek SoC gönderiliyor:", message)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(json.dumps(message).encode())
client.close()
