#!/usr/bin/env python3
"""
Şarj İstasyonu (EVSE) Simülatörü
V2G Protocol Manipulation Simülasyonu

Bu simülatör:
1. CSMS'e bağlanır ve kendini tanıtır
2. EV bağlantısını simüle eder
3. V2G (Vehicle-to-Grid) enerji transferini destekler
4. Şarj/Deşarj durumunu raporlar
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from enum import Enum
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class V2GMode(Enum):
    """V2G Çalışma Modları"""
    IDLE = "idle"
    CHARGING = "charging"      # Şebekeden araca
    DISCHARGING = "discharging"  # Araçtan şebekeye (V2G)


class ChargingStation(cp):
    """OCPP 1.6 Şarj İstasyonu"""
    
    def __init__(self, station_id, websocket):
        super().__init__(station_id, websocket)
        self.station_id = station_id
        self.v2g_mode = V2GMode.IDLE
        self.energy_imported = 0.0  # Wh
        self.energy_exported = 0.0  # Wh
        self.current_power = 0.0    # W
        self.ev_connected = False
        self.ev_soc = 80  # Batarya durumu (%)
        self.max_charge_power = 22000  # W (22 kW)
        self.max_discharge_power = 11000  # W (11 kW)
    
    async def send_boot_notification(self):
        """CSMS'e kendini tanıt"""
        request = call.BootNotification(
            charge_point_model="V2G-Station-Pro",
            charge_point_vendor="BSG-Energy"
        )
        
        logger.info("📡 CSMS'e BootNotification gönderiliyor...")
        
        try:
            response = await self.call(request)
            
            if response.status == RegistrationStatus.accepted:
                logger.info(f"✅ CSMS tarafından kabul edildi!")
                logger.info(f"   Heartbeat aralığı: {response.interval}s")
                return response.interval
            else:
                logger.error(f"❌ CSMS tarafından reddedildi: {response.status}")
                return None
        except Exception as e:
            logger.error(f"❌ BootNotification hatası: {e}")
            return None
    
    async def send_heartbeat_loop(self, interval):
        """Düzenli heartbeat gönder"""
        while True:
            await asyncio.sleep(interval)
            
            request = call.Heartbeat()
            
            try:
                response = await self.call(request)
                logger.debug(f"💓 Heartbeat - Sunucu zamanı: {response.current_time}")
            except Exception as e:
                logger.error(f"❌ Heartbeat hatası: {e}")
    
    async def send_status_notification(self, status):
        """Durum bildirimi gönder"""
        request = call.StatusNotification(
            connector_id=1,
            error_code='NoError',
            status=status
        )
        
        try:
            await self.call(request)
            logger.info(f"📊 Durum güncellendi: {status}")
        except Exception as e:
            logger.error(f"❌ StatusNotification hatası: {e}")
    
    async def send_meter_values(self):
        """Enerji sayaç değerlerini gönder"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        sampled_values = []
        
        # Import (Şebekeden araca)
        if self.v2g_mode == V2GMode.CHARGING:
            sampled_values.append({
                'value': str(int(self.energy_imported)),
                'context': 'Sample.Periodic',
                'format': 'Raw',
                'measurand': 'Energy.Active.Import.Register',
                'unit': 'Wh'
            })
        
        # Export (Araçtan şebekeye - V2G)
        if self.v2g_mode == V2GMode.DISCHARGING:
            sampled_values.append({
                'value': str(int(self.energy_exported)),
                'context': 'Sample.Periodic',
                'format': 'Raw',
                'measurand': 'Energy.Active.Export.Register',
                'unit': 'Wh'
            })
        
        # Anlık güç
        sampled_values.append({
            'value': str(int(abs(self.current_power))),
            'context': 'Sample.Periodic',
            'format': 'Raw',
            'measurand': 'Power.Active.Import' if self.v2g_mode == V2GMode.CHARGING else 'Power.Active.Export',
            'unit': 'W'
        })
        
        meter_value = [{
            'timestamp': timestamp,
            'sampled_value': sampled_values
        }]
        
        request = call.MeterValues(
            connector_id=1,
            meter_value=meter_value
        )
        
        try:
            await self.call(request)
        except Exception as e:
            logger.error(f"❌ MeterValues hatası: {e}")
    
    async def send_v2g_data(self, data):
        """V2G özel verisi gönder"""
        request = call.DataTransfer(
            vendor_id='BSG-Energy',
            message_id='V2G_Status',
            data=json.dumps(data)
        )
        
        try:
            response = await self.call(request)
            if response.status == 'Accepted':
                logger.info(f"📦 V2G verisi gönderildi")
        except Exception as e:
            logger.error(f"❌ DataTransfer hatası: {e}")
    
    async def simulate_charging(self):
        """Şarj simülasyonu"""
        self.v2g_mode = V2GMode.CHARGING
        self.current_power = self.max_charge_power
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔋 ŞARJ BAŞLADI")
        logger.info(f"{'='*60}")
        logger.info(f"   Mod: Grid → Vehicle (G2V)")
        logger.info(f"   Güç: {self.current_power/1000:.1f} kW")
        logger.info(f"   Batarya: {self.ev_soc}%")
        logger.info(f"{'='*60}\n")
        
        await self.send_status_notification('Charging')
        
        while self.ev_soc < 100 and self.v2g_mode == V2GMode.CHARGING:
            await asyncio.sleep(5)
            
            # Enerji hesapla (5 saniyede)
            energy_wh = (self.current_power * 5) / 3600
            self.energy_imported += energy_wh
            self.ev_soc += 0.5  # Her 5 saniyede %0.5
            
            logger.info(f"⚡ Şarj ediyor... SoC: {self.ev_soc:.1f}% | Enerji: {self.energy_imported/1000:.2f} kWh")
            
            await self.send_meter_values()
    
    async def simulate_discharging(self, power_kw=11, duration_min=10):
        """V2G Deşarj simülasyonu (Vehicle-to-Grid)"""
        self.v2g_mode = V2GMode.DISCHARGING
        self.current_power = power_kw * 1000  # kW → W
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔋 V2G DEŞARJ BAŞLADI")
        logger.info(f"{'='*60}")
        logger.info(f"   Mod: Vehicle → Grid (V2G)")
        logger.info(f"   Güç: {power_kw:.1f} kW")
        logger.info(f"   Süre: {duration_min} dakika")
        logger.info(f"   Batarya: {self.ev_soc}%")
        logger.info(f"{'='*60}\n")
        
        await self.send_status_notification('Charging')  # OCPP'de V2G için özel durum yok
        
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + (duration_min * 60)
        
        while asyncio.get_event_loop().time() < end_time and self.ev_soc > 20:
            await asyncio.sleep(5)
            
            # Enerji hesapla
            energy_wh = (self.current_power * 5) / 3600
            self.energy_exported += energy_wh
            self.ev_soc -= 0.3  # Her 5 saniyede %0.3
            
            logger.info(f"⚡ V2G Deşarj... SoC: {self.ev_soc:.1f}% | Şebekeye: {self.energy_exported/1000:.2f} kWh")
            
            await self.send_meter_values()
            
            # V2G durumu gönder
            await self.send_v2g_data({
                'mode': 'V2G',
                'power_kw': power_kw,
                'soc': self.ev_soc,
                'energy_exported_kwh': self.energy_exported / 1000
            })
        
        self.v2g_mode = V2GMode.IDLE
        self.current_power = 0
        logger.info(f"\n✅ V2G deşarj tamamlandı! Toplam: {self.energy_exported/1000:.2f} kWh")
    
    async def start(self):
        """İstasyonu başlat"""
        # Boot notification
        interval = await self.send_boot_notification()
        
        if interval:
            # Durum bildirimi
            await self.send_status_notification('Available')
            
            # EV bağlantısı simüle et
            await asyncio.sleep(3)
            self.ev_connected = True
            logger.info("🔌 EV bağlandı!")
            await self.send_status_notification('Preparing')
            
            # Heartbeat ve simülasyon paralel çalışsın
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self._main_loop(),
                return_exceptions=True
            )
        else:
            logger.error("❌ Boot başarısız, istasyon durduruluyor")
    
    async def _main_loop(self):
        """Ana çalışma döngüsü"""
        await asyncio.sleep(5)
        
        # Önce biraz şarj
        await self.simulate_charging()
        
        await asyncio.sleep(3)
        
        # Sonra V2G deşarj
        await self.simulate_discharging(power_kw=11, duration_min=5)
        
        await self.send_status_notification('Available')
        
        # Bekle
        while True:
            await asyncio.sleep(60)


async def main():
    """Ana program"""
    station_id = "EVSE_001"
    csms_url = f"ws://localhost:9000/{station_id}"
    
    logger.info("="*60)
    logger.info("🔌 ŞARJ İSTASYONU BAŞLATILIYOR")
    logger.info("="*60)
    logger.info(f"   Station ID: {station_id}")
    logger.info(f"   CSMS URL: {csms_url}")
    logger.info(f"   V2G Desteği: Aktif")
    logger.info(f"   Max Şarj: 22 kW")
    logger.info(f"   Max Deşarj (V2G): 11 kW")
    logger.info("="*60)
    
    try:
        async with websockets.connect(
            csms_url,
            subprotocols=['ocpp1.6']
        ) as ws:
            logger.info("✅ CSMS'e bağlandı!")
            
            station = ChargingStation(station_id, ws)
            
            await asyncio.gather(
                cp.start(station),
                station.start(),
                return_exceptions=True
            )
            
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"❌ Bağlantı hatası: CSMS çalışmıyor olabilir ({e})")
    except Exception as e:
        logger.error(f"❌ İstasyon hatası: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 İstasyon kapatıldı")
