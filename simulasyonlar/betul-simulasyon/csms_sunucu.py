# csms_sunucu.py  (OCPP 1.6 uyumlu, v11+ websockets ile)
import asyncio
import websockets

async def on_connect(websocket):
    # websockets v11+ : istasyon kimliğini path'ten al
    # ws://localhost:9000/EVSE-TR-001  -> "EVSE-TR-001"
    cp_id = websocket.request.path.strip("/") or "CP001"
    print(f"🔌 İstasyon '{cp_id}' bağlanıyor...")

    try:
        # İstasyon kapatana kadar gelen mesajları dinle
        async for msg in websocket:
            print(f"[{cp_id}] ➜ {msg}")
            # istersen burada doğrulama/işleme/yanıt gönder
            # await websocket.send("OK")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"ℹ️ İstasyon '{cp_id}' normal kapattı.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"⚠️ İstasyon '{cp_id}' bağlantı hatası: {e}")
    except Exception as e:
        print(f"❌ Genel hata: {e}")

async def main():
    print("🚀 OCPP CSMS 9000 portunda başlatılıyor...")
    server = await websockets.serve(
        on_connect,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"],   # ÖNEMLİ: OCPP alt protokolü
    )
    print("✅ Sunucu hazır. Beklenen adres: ws://localhost:9000/ISTASYON_ID")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
