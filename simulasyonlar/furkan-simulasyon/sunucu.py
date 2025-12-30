import asyncio
import websockets
import json
import time


async def handler(websocket):
    path = websocket.request.path
    print(f"📡 İstasyon bağlandı: {path}")
    try:
        async for message in websocket:
            # Zaman damgası ekleyerek logla
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {message}"

            print(f"📥 Alındı: {message}")

            # CSMS Loguna yaz
            with open("csms_log.txt", "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

    except Exception as e:
        print(f"❌ Hata: {e}")


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("✅ OCPP Sunucusu Aktif. Loglar: csms_log.txt")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())