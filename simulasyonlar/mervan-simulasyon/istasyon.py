import asyncio
import logging
from datetime import datetime
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus
import websockets

logging.basicConfig(level=logging.INFO)

class SarjIstasyonu(cp):
    
    async def send_boot_notification(self):
        """
        İstasyon ilk açıldığında CSMS'e kendini tanıtır
        """
        # OCPP 1.6 için call() metodunu kullanıyoruz
        request = call.BootNotification(
            charge_point_model="Model-X",
            charge_point_vendor="MyCompany"
        )
        
        print("📡 CSMS'e BootNotification gönderiliyor...")
        
        try:
            response = await self.call(request)
            
            if response.status == RegistrationStatus.accepted:
                print(f"✅ CSMS tarafından kabul edildi! Heartbeat aralığı: {response.interval}s")
                return response.interval
            else:
                print(f"❌ CSMS tarafından reddedildi: {response.status}")
                return None
        except Exception as e:
            print(f"❌ BootNotification hatası: {e}")
            return None
    
    async def send_heartbeat_loop(self, interval):
        """
        Düzenli olarak CSMS'e 'hayattayım' mesajı gönderir
        """
        while True:
            await asyncio.sleep(interval)
            
            request = call.Heartbeat()
            
            try:
                response = await self.call(request)
                print(f"💓 Heartbeat gönderildi, CSMS zamanı: {response.current_time}")
            except Exception as e:
                print(f"❌ Heartbeat hatası: {e}")
    
    async def send_meter_values_loop(self):
        """
        Sürekli şarj verisi gönderir (Anomali tespiti için kullanılacak)
        """
        enerji = 1000  # Wh cinsinden başlangıç enerjisi
        
        await asyncio.sleep(5)  # Boot'tan sonra biraz bekle
        
        while True:
            await asyncio.sleep(10)  # 10 saniye bekle
            enerji += 50  # Her 10 saniyede 50 Wh enerji harcanmış gibi yap
            
            print(f"\n⚡ İSTASYON: CSMS'e 'Şarj Ediyorum' verisi gönderiliyor (Değer: {enerji} Wh)")
            
            # OCPP 1.6 için basitleştirilmiş format
            meter_value = [{
                'timestamp': datetime.utcnow().isoformat(),
                'sampled_value': [{
                    'value': str(enerji),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Energy.Active.Import.Register',
                    'unit': 'Wh'
                }]
            }]
            
            # MeterValues mesajını gönder
            request = call.MeterValues(
                connector_id=1,
                meter_value=meter_value
            )
            
            try:
                await self.call(request)
            except Exception as e:
                print(f"❌ MeterValues gönderme hatası: {e}")
    
    async def start(self):
        """
        İstasyonu başlat: Boot -> Heartbeat -> MeterValues
        """
        # 1. Boot notification gönder
        interval = await self.send_boot_notification()
        
        if interval:
            # 2. Heartbeat ve MeterValues döngülerini paralel başlat
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self.send_meter_values_loop(),
                return_exceptions=True  # Bir hata diğerini durdurmasın
            )
        else:
            print("❌ Boot notification başarısız, istasyon durduruluyor")

async def main():
    # CSMS sunucusuna bağlan
    try:
        async with websockets.connect(
            'ws://localhost:9000/CP001',  # İstasyon ID'si: CP001
            subprotocols=['ocpp1.6']
        ) as ws:
            
            print("🔌 CSMS sunucusuna bağlanıldı!")
            
            # ChargePoint örneği oluştur
            charge_point = SarjIstasyonu('CP001', ws)
            
            # Paralel olarak çalıştır:
            # 1. cp.start() - OCPP mesajlarını dinler ve yanıtlar
            # 2. charge_point.start() - Boot/Heartbeat/MeterValues gönderir
            await asyncio.gather(
                cp.start(charge_point),  # Gelen mesajları dinle
                charge_point.start(),  # Mesaj gönder
                return_exceptions=True
            )
            
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Bağlantı hatası: CSMS sunucusu çalışmıyor olabilir ({e})")
    except Exception as e:
        print(f"❌ İstasyon hatası: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 İstasyon kapatıldı")
