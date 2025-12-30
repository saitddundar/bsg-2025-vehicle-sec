#!/usr/bin/env python3
"""
CSMS (Central System Management Server) - OCPP 1.6
V2G Protocol Manipulation Simülasyonu için Merkezi Sunucu

Bu sunucu:
1. Şarj istasyonlarından gelen bağlantıları kabul eder
2. V2G (Vehicle-to-Grid) enerji transfer komutlarını koordine eder
3. Mikro şebeke durumunu izler
"""

import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
import json
import websockets
from ocpp.v16 import call_result, call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus
from ocpp.routing import on

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MicrogridState:
    """Mikro şebeke durumu"""
    def __init__(self):
        self.frequency = 50.0  # Hz (Nominal)
        self.voltage = 230.0   # V (Nominal)
        self.total_load = 0.0  # kW
        self.v2g_power = 0.0   # kW (negatif: araçtan şebekeye)
        self.connected_evs = {}
        self.alerts = []
    
    def to_dict(self):
        return {
            'frequency': self.frequency,
            'voltage': self.voltage,
            'total_load': self.total_load,
            'v2g_power': self.v2g_power,
            'connected_evs': len(self.connected_evs),
            'status': 'ANOMALY' if self.alerts else 'NORMAL'
        }


# Global mikro şebeke durumu
microgrid = MicrogridState()


class ChargePointHandler(cp):
    """OCPP 1.6 Şarj İstasyonu Yöneticisi"""
    
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.energy_imported = 0  # Wh
        self.energy_exported = 0  # Wh (V2G)
        self.current_power = 0    # W
        self.v2g_enabled = False
    
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        """Şarj istasyonu başlatıldığında"""
        logger.info(f"🔌 İSTASYON BAĞLANDI: {self.id}")
        logger.info(f"   Üretici: {charge_point_vendor}")
        logger.info(f"   Model: {charge_point_model}")
        
        microgrid.connected_evs[self.id] = {
            'vendor': charge_point_vendor,
            'model': charge_point_model,
            'connected_at': datetime.now(timezone.utc).isoformat(),
            'status': 'Available'
        }
        
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )
    
    @on('Heartbeat')
    async def on_heartbeat(self):
        """Heartbeat - İstasyon hala aktif"""
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat()
        )
    
    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        """İstasyon durum bildirimi"""
        logger.info(f"📊 DURUM DEĞİŞİKLİĞİ: {self.id}")
        logger.info(f"   Connector: {connector_id}")
        logger.info(f"   Status: {status}")
        
        if self.id in microgrid.connected_evs:
            microgrid.connected_evs[self.id]['status'] = status
        
        return call_result.StatusNotification()
    
    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        """Sayaç değerleri - Enerji akışı"""
        for val in meter_value:
            for sample in val.get('sampled_value', []):
                measurand = sample.get('measurand', 'Energy.Active.Import.Register')
                value = float(sample.get('value', 0))
                unit = sample.get('unit', 'Wh')
                
                # V2G tespit et
                if 'Export' in measurand:
                    self.energy_exported = value
                    power_direction = "→ ŞEBEKe (V2G)"
                    microgrid.v2g_power = value / 1000  # kW
                else:
                    self.energy_imported = value
                    power_direction = "← ARAÇ"
                
                logger.info(f"⚡ ENERJİ AKIŞI: {self.id}")
                logger.info(f"   Measurand: {measurand}")
                logger.info(f"   Değer: {value} {unit}")
                logger.info(f"   Yön: {power_direction}")
                
                # Anomali kontrolü
                self._check_v2g_anomaly(measurand, value)
        
        return call_result.MeterValues()
    
    @on('DataTransfer')
    async def on_data_transfer(self, vendor_id, message_id=None, data=None):
        """Özel veri transferi - V2G komutları için"""
        logger.info(f"📦 DATA TRANSFER: {self.id}")
        logger.info(f"   Vendor: {vendor_id}")
        logger.info(f"   Message ID: {message_id}")
        
        try:
            if data:
                payload = json.loads(data) if isinstance(data, str) else data
                logger.info(f"   Data: {json.dumps(payload, indent=2)}")
                
                # V2G komutlarını işle
                if message_id == 'V2G_SetDischargeSchedule':
                    return await self._handle_v2g_schedule(payload)
                elif message_id == 'V2G_StartDischarge':
                    return await self._handle_v2g_start(payload)
        except json.JSONDecodeError:
            logger.warning(f"   Raw Data: {data}")
        
        return call_result.DataTransfer(status='Accepted')
    
    async def _handle_v2g_schedule(self, payload):
        """V2G deşarj programını işle"""
        schedule = payload.get('schedule', [])
        logger.info(f"🔋 V2G PROGRAM ALINDI: {self.id}")
        
        for slot in schedule:
            start = slot.get('start_time')
            end = slot.get('end_time')
            power = slot.get('power_kw', 0)
            logger.info(f"   {start} - {end}: {power} kW")
        
        self.v2g_enabled = True
        return call_result.DataTransfer(status='Accepted', data=json.dumps({
            'v2g_status': 'scheduled',
            'slots': len(schedule)
        }))
    
    async def _handle_v2g_start(self, payload):
        """V2G deşarj başlat"""
        power_kw = payload.get('power_kw', 0)
        duration_min = payload.get('duration_minutes', 60)
        
        logger.info(f"🔋 V2G DEŞARJ BAŞLADI: {self.id}")
        logger.info(f"   Güç: {power_kw} kW")
        logger.info(f"   Süre: {duration_min} dakika")
        
        # Mikro şebeke güncelle
        microgrid.v2g_power += power_kw
        microgrid.total_load -= power_kw  # V2G yük azaltır
        
        return call_result.DataTransfer(status='Accepted', data=json.dumps({
            'v2g_status': 'discharging',
            'power_kw': power_kw
        }))
    
    def _check_v2g_anomaly(self, measurand, value):
        """V2G anomalisi kontrolü"""
        # Ani yüksek enerji transferi
        if 'Export' in measurand and value > 50000:  # 50 kWh üzeri
            alert = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'station_id': self.id,
                'type': 'HIGH_V2G_EXPORT',
                'value': value,
                'message': f'Anormal yüksek V2G enerji transferi: {value} Wh'
            }
            microgrid.alerts.append(alert)
            logger.warning(f"🚨 ANOMALİ: {alert['message']}")


async def on_connect(websocket):
    """Yeni bağlantı işleyicisi"""
    try:
        # websockets v11+ için path alma
        charge_point_id = websocket.request.path.strip('/')
        
        if not charge_point_id:
            charge_point_id = f"CP_{datetime.now().strftime('%H%M%S')}"
            logger.warning(f"⚠️ Path boş, varsayılan ID: {charge_point_id}")
        
        logger.info(f"🔗 Bağlantı isteği: {charge_point_id}")
        
        cp_handler = ChargePointHandler(charge_point_id, websocket)
        
        await cp_handler.start()
        
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"ℹ️ {charge_point_id} bağlantıyı kapattı")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(f"⚠️ {charge_point_id} bağlantı hatası: {e}")
    except Exception as e:
        logger.error(f"❌ Bağlantı hatası: {e}", exc_info=True)
    finally:
        # Bağlı EV'leri temizle
        if charge_point_id in microgrid.connected_evs:
            del microgrid.connected_evs[charge_point_id]


async def microgrid_status_task():
    """Periyodik mikro şebeke durumu yazdır"""
    while True:
        await asyncio.sleep(15)
        
        status = microgrid.to_dict()
        logger.info(f"\n{'='*60}")
        logger.info(f"🌐 MİKRO ŞEBEKE DURUMU")
        logger.info(f"{'='*60}")
        logger.info(f"   Frekans: {status['frequency']:.2f} Hz")
        logger.info(f"   Voltaj: {status['voltage']:.1f} V")
        logger.info(f"   Toplam Yük: {status['total_load']:.2f} kW")
        logger.info(f"   V2G Güç: {status['v2g_power']:.2f} kW")
        logger.info(f"   Bağlı EV: {status['connected_evs']}")
        logger.info(f"   Durum: {status['status']}")
        
        if microgrid.alerts:
            logger.warning(f"   ⚠️ Aktif Uyarı: {len(microgrid.alerts)}")
        logger.info(f"{'='*60}\n")


async def main():
    """Ana sunucu başlatma"""
    logger.info("="*60)
    logger.info("🔋 V2G CSMS SUNUCUSU BAŞLATILIYOR")
    logger.info("="*60)
    logger.info("Protokol: OCPP 1.6")
    logger.info("Port: 9000")
    logger.info("V2G Desteği: Aktif")
    logger.info("="*60)
    
    # WebSocket sunucusu
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )
    
    logger.info("✅ Sunucu başarıyla başlatıldı!")
    logger.info("📡 Bağlantı için: ws://localhost:9000/STATION_ID")
    logger.info("")
    
    # Mikro şebeke izleme görevi
    status_task = asyncio.create_task(microgrid_status_task())
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("\n👋 Sunucu kapatılıyor...")
        status_task.cancel()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Sunucu kapatıldı")
