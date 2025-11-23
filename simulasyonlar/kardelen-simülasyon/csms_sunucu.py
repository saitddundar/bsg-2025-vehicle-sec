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

        # --- [KARDELEN] ANOMALİ SENARYOSU BAŞLANGICI ---
        async def send_attack_message():
            await asyncio.sleep(5) 
            
            print(f"🔥🔥🔥 [ANOMALİ SENARYOSU] {self.id} İÇİN SALDIRI BAŞLATILIYOR: SetDisplayMessage")
            
            # --- [DÜZELTME] ---
            # 'AttributeError' hatasını aşmak için saldırıyı manuel (sözlük/dict) olarak oluşturuyoruz.
            action = "SetDisplayMessage"
            payload = {
                "message": "FİYATLAR 0 TL! HACKLENDINIZ!"
            }
            # --- DÜZELTME SONU ---
            
            try:
                # Sunucudan istasyona 'call' (arama) yapıyoruz
                response = await self.call(action, payload)
                
                print(f"✅ [ANOMALİ] {self.id} EKRAN DEĞİŞTİRME YANITI: {response.status}")
            except Exception as e:
                print(f"⚠️ [ANOMALİ] {self.id} saldırısı gönderilirken hata: {e}")

        asyncio.create_task(send_attack_message())
        # --- [KARDELEN] ANOMALİ SENARYOSU SONU ---

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

async def on_connect(websocket):
    try:
        charge_point_id = websocket.request.path.strip('/')
        
        if not charge_point_id:
            charge_point_id = "CP001"
            print(f"⚠️  Path boş, varsayılan ID kullanılıyor: {charge_point_id}")
        
        cp_instance = SarjIstasyonuYonetimi(charge_point_id, websocket)
        
        print(f"✅ İstasyon '{charge_point_id}' bağlantı kuruyor...")
        
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