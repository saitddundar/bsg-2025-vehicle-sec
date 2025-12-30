import asyncio
import websockets
import json
import time


async def send_data():
    uri = "ws://localhost:8765/CP_001"
    async with websockets.connect(uri) as websocket:
        mod = "attack"  # Veya "normal"

        while True:
            payload = {
                "status": "Uploaded",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "vendor": "Wallbox-X"
            }
            if mod == "attack":
                payload["diag_ext"] = "b1"

            message = json.dumps(payload)
            await websocket.send(message)

            # İstasyonun kendi logu
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open("istasyon_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] MOD: {mod.upper()} | GÖNDERİLDİ: {message}\n")

            print(f"📤 Gönderildi ({mod})")
            await asyncio.sleep(5)


asyncio.run(send_data())