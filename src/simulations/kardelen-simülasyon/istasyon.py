import asyncio
import logging
from datetime import datetime
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call, call_result
from ocpp.v16.enums import RegistrationStatus
from ocpp.routing import on
import websockets
import sys  # <-- Programı durdurmak için eklendi

logging.basicConfig(level=logging.INFO)

class SarjIstasyonu(cp):
    
    @on('SetDisplayMessage')
    async def on_set_display_message(self, message, **kwargs):
        """
        CSMS'ten gelen SetDisplayMessage komutunu işler.
        Bu, bizim anomali senaryomuzun 'Etki (Defacement)' aşamasıdır.
        """
        
        # Gelen mesajı terminale basarak "ekranın hacklendiğini" simüle ediyoruz
        print("\n" + "="*50)
        print("🔥🔥🔥 [ANOMALİ SALDIRISI ALINDI!] 🔥🔥🔥")
        print(f"ISTASYON EKRANI GÜNCELLENDİ: \n>>> {message}")
        print("="*50 + "\n")
        
        print("✅ Anomali alındı, istasyon simülasyonu durduruluyor.")
        sys.exit()  # Programı sonlandırır

        # --- [DÜZELTME] ---
        # Hata veren 'enum' (SetDisplayMessageStatus) yerine basit bir 
        # string ('Accepted') gönderiyoruz. Bu, her sürümde çalışır.
        return call_result.SetDisplayMessage(
            status="Accepted"
        )
    
    async def send_boot_notification(self):
        """
        İstasyon ilk açıldığında CSMS'e kendini tanıtır
        """
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
        Sürekli şarj verisi gönderir
        """
        enerji = 1000
        await asyncio.sleep(5)
        
        while True:
            await asyncio.sleep(10)
            enerji += 50
            print(f"\n⚡ İSTASYON: CSMS'e 'Şarj Ediyorum' verisi gönderiliyor (Değer: {enerji} Wh)")
            
            meter_value = [{
                'timestamp': datetime.utcnow().isoformat(),
                'sampled_value': [{'value': str(enerji), 'context': 'Sample.Periodic', 'format': 'Raw', 'measurand': 'Energy.Active.Import.Register', 'unit': 'Wh'}]
            }]
            
            request = call.MeterValues(connector_id=1, meter_value=meter_value)
            
            try:
                await self.call(request)
            except Exception as e:
                print(f"❌ MeterValues gönderme hatası: {e}")
    
    async def start(self):
        interval = await self.send_boot_notification()
        if interval:
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self.send_meter_values_loop(),
                return_exceptions=True
            )
        else:
            print("❌ Boot notification başarısız, istasyon durduruluyor")

async def main():
    try:
        async with websockets.connect(
            'ws://localhost:9000/CP001',
            subprotocols=['ocpp1.6']
        ) as ws:
            print("🔌 CSMS sunucusuna bağlanıldı!")
            charge_point = SarjIstasyonu('CP001', ws)
            await asyncio.gather(
                cp.start(charge_point),
                charge_point.start(),
                return_exceptions=True
            )
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Bağlantı hatası: CSMS sunucusu çalışmıyor olabilir ({e})")
    except SystemExit: # <-- sys.exit() çağrıldığında temiz kapanış yap
        print("👋 Anomali testi tamamlandı. İstasyon kapatıldı.")
    except Exception as e:
        print(f"❌ İstasyon hatası: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 İstasyon manuel olarak kapatıldı")