import asyncio
import logging
from datetime import datetime, timezone
import websockets
from ocpp.v16 import call_result
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus
from ocpp.routing import on

logging.basicConfig(level=logging.INFO)

class SarjIstasyonuYonetimi(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        print(f"İSTASYON BAĞLANDI: {self.id}")
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )
    
    @on('Heartbeat')
    async def on_heartbeat(self):
        print(f"Heartbeat alındı: {self.id}")
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat()
        )
    
    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        for val in meter_value:
            print(f">>> YZ (AI) İÇİN GİRİŞ VERİSİ (OCPP): {self.id} şarj oluyor, Değer: {val['sampled_value'][0]['value']}")
        return call_result.MeterValues()

# DÜZELTME: websockets v11+ için request.path kullanılıyor
async def on_connect(websocket):
    """
    Yeni bağlanan her şarj istasyonu için bir ChargePoint
    örneği oluşturur ve mesajları dinlemeye başlar.
    """
    try:
        # websockets v11+ için request.path kullanılıyor
        charge_point_id = websocket.request.path.strip('/')
        
        # Eğer path boşsa varsayılan ID kullan
        if not charge_point_id:
            charge_point_id = "CP001"
            print(f"⚠️  Path boş, varsayılan ID kullanılıyor: {charge_point_id}")
        
        cp_instance = SarjIstasyonuYonetimi(charge_point_id, websocket)
        
        print(f"✅ İstasyon '{charge_point_id}' bağlantı kuruyor...")
        
        # DÜZELTME: start() fonksiyonu bağlantı açık kaldığı sürece çalışır
        # Bağlantı kapanana kadar bekle
        await cp_instance.start()
        
    except websockets.exceptions.ConnectionClosedOK:
        print(f"ℹ️  İstasyon '{charge_point_id}' bağlantıyı kapattı (normal)")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"⚠️  İstasyon '{charge_point_id}' bağlantı hatası: {e}")
    except Exception as e:
        logging.error(f"Bağlantı hatası: {e}", exc_info=True)

async def main():
    logging.info("OCPP CSMS Sunucusu 9000 portunda başlatılıyor...")
    
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )
    
    print("✅ Sunucu başarıyla başlatıldı ve bağlantı bekliyor...")
    print("📡 Bağlantı için: ws://localhost:9000/ISTASYON_ID")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
