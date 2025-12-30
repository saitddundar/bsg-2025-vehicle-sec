#!/usr/bin/env python3
"""
Mikro Şebeke İzleme ve Anomali Tespit Sistemi
V2G Protocol Manipulation Simülasyonu

Bu sistem:
1. Mikro şebeke parametrelerini izler (voltaj, frekans, güç)
2. V2G enerji akışlarını takip eder
3. Anormal durumları tespit eder
4. Saldırı tespiti yapar
"""

import asyncio
import logging
import random
import math
from datetime import datetime
from enum import Enum
from collections import deque

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Uyarı seviyeleri"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ATTACK = "ATTACK"


class MicrogridMonitor:
    """Mikro Şebeke İzleme Sistemi"""
    
    def __init__(self):
        # Nominal değerler
        self.NOMINAL_FREQUENCY = 50.0  # Hz
        self.NOMINAL_VOLTAGE = 230.0   # V
        
        # Toleranslar
        self.FREQ_TOLERANCE = 0.5  # ±0.5 Hz
        self.VOLTAGE_TOLERANCE = 23.0  # ±23V (%10)
        
        # Mevcut değerler
        self.frequency = 50.0
        self.voltage = 230.0
        self.total_load = 100.0  # kW (temel yük)
        self.total_generation = 120.0  # kW
        self.v2g_power = 0.0  # kW
        
        # EV'ler
        self.connected_evs = {}
        self.ev_v2g_power = {}  # Her EV'nin V2G gücü
        
        # Geçmiş veriler (anomali tespiti için)
        self.frequency_history = deque(maxlen=60)
        self.voltage_history = deque(maxlen=60)
        self.v2g_history = deque(maxlen=60)
        
        # Anomali sayaçları
        self.total_checks = 0
        self.anomaly_count = 0
        self.attack_indicators = []
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 MİKRO ŞEBEKE İZLEME SİSTEMİ BAŞLATILDI")
        logger.info(f"{'='*70}")
        logger.info(f"   Nominal Frekans: {self.NOMINAL_FREQUENCY} Hz")
        logger.info(f"   Nominal Voltaj: {self.NOMINAL_VOLTAGE} V")
        logger.info(f"   Frekans Toleransı: ±{self.FREQ_TOLERANCE} Hz")
        logger.info(f"   Voltaj Toleransı: ±{self.VOLTAGE_TOLERANCE} V")
        logger.info(f"{'='*70}\n")
    
    def add_ev(self, ev_id, max_power_kw=11):
        """EV bağlantısı ekle"""
        self.connected_evs[ev_id] = {
            'connected_at': datetime.now().isoformat(),
            'max_power_kw': max_power_kw,
            'current_power_kw': 0,
            'mode': 'idle'
        }
        self.ev_v2g_power[ev_id] = 0
        logger.info(f"🔌 EV Bağlandı: {ev_id} (Max: {max_power_kw} kW)")
    
    def remove_ev(self, ev_id):
        """EV bağlantısını kaldır"""
        if ev_id in self.connected_evs:
            del self.connected_evs[ev_id]
            del self.ev_v2g_power[ev_id]
            logger.info(f"🔌 EV Ayrıldı: {ev_id}")
    
    def update_v2g_power(self, ev_id, power_kw):
        """EV'nin V2G gücünü güncelle"""
        if ev_id in self.connected_evs:
            self.ev_v2g_power[ev_id] = power_kw
            self.connected_evs[ev_id]['current_power_kw'] = power_kw
            self.connected_evs[ev_id]['mode'] = 'v2g' if power_kw > 0 else 'idle'
    
    def simulate_grid_dynamics(self):
        """Şebeke dinamiklerini simüle et"""
        # Toplam V2G gücü
        self.v2g_power = sum(self.ev_v2g_power.values())
        
        # Güç dengesi
        power_balance = self.total_generation + self.v2g_power - self.total_load
        
        # Frekans sapması (güç dengesine göre)
        # Pozitif denge → frekans artar, negatif → azalır
        freq_deviation = power_balance * 0.01  # Basit model
        self.frequency = self.NOMINAL_FREQUENCY + freq_deviation + random.uniform(-0.1, 0.1)
        
        # Voltaj sapması
        voltage_deviation = power_balance * 0.1 + random.uniform(-2, 2)
        self.voltage = self.NOMINAL_VOLTAGE + voltage_deviation
        
        # Geçmişe ekle
        self.frequency_history.append(self.frequency)
        self.voltage_history.append(self.voltage)
        self.v2g_history.append(self.v2g_power)
    
    def detect_anomaly(self):
        """Anomali tespit et"""
        self.total_checks += 1
        anomalies = []
        
        # 1. Frekans sapması kontrolü
        freq_deviation = abs(self.frequency - self.NOMINAL_FREQUENCY)
        if freq_deviation > self.FREQ_TOLERANCE:
            anomalies.append({
                'type': 'FREQUENCY_DEVIATION',
                'level': AlertLevel.WARNING if freq_deviation < 1.0 else AlertLevel.CRITICAL,
                'value': self.frequency,
                'deviation': freq_deviation,
                'message': f'Frekans sapması: {self.frequency:.2f} Hz (Sapma: {freq_deviation:.2f} Hz)'
            })
        
        # 2. Voltaj sapması kontrolü
        voltage_deviation = abs(self.voltage - self.NOMINAL_VOLTAGE)
        if voltage_deviation > self.VOLTAGE_TOLERANCE:
            anomalies.append({
                'type': 'VOLTAGE_DEVIATION',
                'level': AlertLevel.WARNING if voltage_deviation < 30 else AlertLevel.CRITICAL,
                'value': self.voltage,
                'deviation': voltage_deviation,
                'message': f'Voltaj sapması: {self.voltage:.1f} V (Sapma: {voltage_deviation:.1f} V)'
            })
        
        # 3. Ani V2G değişimi kontrolü
        if len(self.v2g_history) >= 5:
            recent_v2g = list(self.v2g_history)[-5:]
            v2g_change = max(recent_v2g) - min(recent_v2g)
            if v2g_change > 30:  # 30 kW'dan fazla ani değişim
                anomalies.append({
                    'type': 'RAPID_V2G_CHANGE',
                    'level': AlertLevel.WARNING,
                    'value': v2g_change,
                    'message': f'Ani V2G güç değişimi: {v2g_change:.1f} kW'
                })
        
        # 4. Koordineli saldırı tespiti
        active_v2g_count = sum(1 for p in self.ev_v2g_power.values() if p > 0)
        if active_v2g_count >= 3 and self.v2g_power > 50:
            anomalies.append({
                'type': 'COORDINATED_V2G',
                'level': AlertLevel.ATTACK,
                'value': active_v2g_count,
                'message': f'Koordineli V2G tespiti: {active_v2g_count} EV aynı anda deşarj ({self.v2g_power:.1f} kW)'
            })
        
        # 5. Aşırı V2G gücü
        if self.v2g_power > 100:  # 100 kW üzeri
            anomalies.append({
                'type': 'EXCESSIVE_V2G',
                'level': AlertLevel.CRITICAL,
                'value': self.v2g_power,
                'message': f'Aşırı V2G gücü: {self.v2g_power:.1f} kW'
            })
        
        if anomalies:
            self.anomaly_count += 1
        
        return anomalies
    
    def detect_attack_pattern(self, anomalies):
        """Saldırı paternlerini tespit et"""
        attack_detected = False
        attack_type = None
        
        # Pattern 1: Sinusoidal V2G manipülasyonu (şebeke dengesizliği hedefli)
        if len(self.v2g_history) >= 10:
            v2g_list = list(self.v2g_history)[-10:]
            oscillation_count = sum(1 for i in range(1, len(v2g_list)) 
                                   if (v2g_list[i] > 0) != (v2g_list[i-1] > 0))
            if oscillation_count >= 4:
                attack_detected = True
                attack_type = "V2G_OSCILLATION_ATTACK"
                self.attack_indicators.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': attack_type,
                    'message': 'V2G güç osilasyonu tespit edildi - Şebeke dengesizliği saldırısı!'
                })
        
        # Pattern 2: Eşzamanlı yüksek V2G
        critical_count = sum(1 for a in anomalies if a['level'] in [AlertLevel.CRITICAL, AlertLevel.ATTACK])
        if critical_count >= 2:
            attack_detected = True
            attack_type = "COORDINATED_DESTABILIZATION"
            self.attack_indicators.append({
                'timestamp': datetime.now().isoformat(),
                'type': attack_type,
                'message': 'Koordineli şebeke dengesizliği saldırısı tespit edildi!'
            })
        
        return attack_detected, attack_type
    
    def print_status(self, anomalies=None):
        """Durum raporu yazdır"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Durum belirleme
        if any(a['level'] == AlertLevel.ATTACK for a in (anomalies or [])):
            status_icon = "🚨"
            status_text = "SALDIRI"
        elif any(a['level'] == AlertLevel.CRITICAL for a in (anomalies or [])):
            status_icon = "⛔"
            status_text = "KRİTİK"
        elif any(a['level'] == AlertLevel.WARNING for a in (anomalies or [])):
            status_icon = "⚠️"
            status_text = "UYARI"
        else:
            status_icon = "✅"
            status_text = "NORMAL"
        
        print(f"\n{'='*70}")
        print(f"[{timestamp}] {status_icon} MİKRO ŞEBEKE DURUMU: {status_text}")
        print(f"{'='*70}")
        
        # Temel parametreler
        freq_status = "✅" if abs(self.frequency - 50) < self.FREQ_TOLERANCE else "⚠️"
        volt_status = "✅" if abs(self.voltage - 230) < self.VOLTAGE_TOLERANCE else "⚠️"
        
        print(f"\n📊 ŞEBEKE PARAMETRELERİ:")
        print(f"   {freq_status} Frekans: {self.frequency:.2f} Hz (Nominal: {self.NOMINAL_FREQUENCY} Hz)")
        print(f"   {volt_status} Voltaj: {self.voltage:.1f} V (Nominal: {self.NOMINAL_VOLTAGE} V)")
        print(f"   📈 Yük: {self.total_load:.1f} kW")
        print(f"   ⚡ Üretim: {self.total_generation:.1f} kW")
        print(f"   🔋 V2G Toplam: {self.v2g_power:.1f} kW")
        
        # Bağlı EV'ler
        print(f"\n🚗 BAĞLI EV'LER ({len(self.connected_evs)}):")
        if self.connected_evs:
            for ev_id, ev_info in self.connected_evs.items():
                power = self.ev_v2g_power.get(ev_id, 0)
                mode = "V2G" if power > 0 else "IDLE"
                print(f"   ├─ {ev_id}: {mode} ({power:.1f} kW)")
        else:
            print(f"   └─ Bağlı EV yok")
        
        # Anomaliler
        if anomalies:
            print(f"\n🔔 TESPİT EDİLEN ANOMALİLER:")
            for a in anomalies:
                level_icon = {
                    AlertLevel.INFO: "ℹ️",
                    AlertLevel.WARNING: "⚠️",
                    AlertLevel.CRITICAL: "⛔",
                    AlertLevel.ATTACK: "🚨"
                }.get(a['level'], "❓")
                print(f"   {level_icon} [{a['level'].value}] {a['message']}")
        
        # Saldırı göstergeleri
        if self.attack_indicators:
            print(f"\n{'🚨'*20}")
            print(f"⚠️  SALDIRI TESPİT EDİLDİ!")
            for indicator in self.attack_indicators[-3:]:  # Son 3 gösterge
                print(f"   └─ {indicator['type']}: {indicator['message']}")
            print(f"{'🚨'*20}")
        
        # İstatistikler
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"\n📈 İSTATİSTİKLER:")
        print(f"   ├─ Toplam Kontrol: {self.total_checks}")
        print(f"   ├─ Anomali Sayısı: {self.anomaly_count}")
        print(f"   └─ Anomali Oranı: {anomaly_rate:.1f}%")
        
        print(f"{'='*70}\n")
    
    async def monitor(self, interval=2):
        """İzleme döngüsü"""
        logger.info("🔍 İzleme başlatılıyor...\n")
        
        try:
            while True:
                # Şebeke dinamiklerini simüle et
                self.simulate_grid_dynamics()
                
                # Anomali tespit et
                anomalies = self.detect_anomaly()
                
                # Saldırı paterni kontrolü
                attack_detected, attack_type = self.detect_attack_pattern(anomalies)
                
                # Durum yazdır
                self.print_status(anomalies)
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n👋 İzleme durduruldu")
            self._print_summary()
    
    def _print_summary(self):
        """Özet rapor"""
        print(f"\n{'='*70}")
        print(f"📊 ÖZET RAPOR")
        print(f"{'='*70}")
        print(f"   Toplam Kontrol: {self.total_checks}")
        print(f"   Tespit Edilen Anomali: {self.anomaly_count}")
        print(f"   Saldırı Göstergesi: {len(self.attack_indicators)}")
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"   Anomali Oranı: {anomaly_rate:.1f}%")
        print(f"{'='*70}\n")


async def demo_attack_scenario(monitor):
    """Demo saldırı senaryosu"""
    await asyncio.sleep(5)
    
    logger.info("\n" + "🎭"*30)
    logger.info("DEMO: Normal operasyon başlıyor...")
    logger.info("🎭"*30 + "\n")
    
    # Normal EV'ler ekle
    monitor.add_ev("EV_001", 11)
    monitor.add_ev("EV_002", 22)
    await asyncio.sleep(10)
    
    # Normal V2G
    monitor.update_v2g_power("EV_001", 5)
    await asyncio.sleep(10)
    
    logger.info("\n" + "🚨"*30)
    logger.info("DEMO: V2G Saldırısı başlıyor...")
    logger.info("🚨"*30 + "\n")
    
    # Saldırı: Birden fazla EV koordineli deşarj
    monitor.add_ev("EV_003", 11)
    monitor.add_ev("EV_004", 11)
    monitor.add_ev("EV_005", 11)
    
    await asyncio.sleep(3)
    
    # Ani yüksek V2G
    monitor.update_v2g_power("EV_001", 11)
    monitor.update_v2g_power("EV_002", 22)
    monitor.update_v2g_power("EV_003", 11)
    monitor.update_v2g_power("EV_004", 11)
    monitor.update_v2g_power("EV_005", 11)
    
    await asyncio.sleep(20)
    
    # V2G osilasyonu (şebeke dengesizliği saldırısı)
    for i in range(10):
        if i % 2 == 0:
            monitor.update_v2g_power("EV_001", 11)
            monitor.update_v2g_power("EV_002", 22)
        else:
            monitor.update_v2g_power("EV_001", 0)
            monitor.update_v2g_power("EV_002", 0)
        await asyncio.sleep(3)


async def main():
    """Ana program"""
    import sys
    
    monitor = MicrogridMonitor()
    
    # Demo modunda mı çalışacak?
    demo_mode = "--demo" in sys.argv
    
    if demo_mode:
        logger.info("🎭 DEMO MODU AKTİF")
        tasks = [
            monitor.monitor(interval=2),
            demo_attack_scenario(monitor)
        ]
    else:
        # Basit simülasyon
        monitor.add_ev("EV_NORMAL_001", 11)
        monitor.update_v2g_power("EV_NORMAL_001", 5)
        tasks = [monitor.monitor(interval=3)]
    
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program sonlandırıldı")
