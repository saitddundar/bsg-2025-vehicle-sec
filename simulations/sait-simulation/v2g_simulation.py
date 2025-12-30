#!/usr/bin/env python3
"""
V2G Protocol Manipulation - Birleşik Simülasyon
Tüm bileşenleri tek bir terminal penceresinde çalıştırır.

Bu script:
1. CSMS sunucusunu başlatır
2. Mikro şebeke izleyicisini başlatır
3. Normal şarj istasyonu simüle eder
4. Saldırı senaryosunu çalıştırır
"""

import asyncio
import logging
import json
import random
import math
from datetime import datetime, timezone
from enum import Enum
from collections import deque

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] %(message)s'
)


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ATTACK = "ATTACK"


class MicrogridState:
    """Mikro şebeke durumu"""
    def __init__(self):
        self.frequency = 50.0
        self.voltage = 230.0
        self.total_load = 100.0
        self.total_generation = 110.0
        self.v2g_power = 0.0
        self.connected_evs = {}
        self.energy_flows = {}
        self.alerts = []
        
        # Geçmiş veriler
        self.freq_history = deque(maxlen=30)
        self.voltage_history = deque(maxlen=30)
        self.v2g_history = deque(maxlen=30)
        
        # İstatistikler
        self.total_checks = 0
        self.anomaly_count = 0
        self.attack_detected = False
    
    def add_ev(self, ev_id, mode='charging', power_kw=0):
        self.connected_evs[ev_id] = {
            'mode': mode,
            'power_kw': power_kw,
            'connected_at': datetime.now().strftime('%H:%M:%S')
        }
        self.energy_flows[ev_id] = power_kw
    
    def update_v2g(self, ev_id, power_kw):
        if ev_id in self.connected_evs:
            self.connected_evs[ev_id]['power_kw'] = power_kw
            self.connected_evs[ev_id]['mode'] = 'v2g' if power_kw > 0 else 'charging'
            self.energy_flows[ev_id] = power_kw
    
    def calculate_grid_state(self):
        """Şebeke durumunu hesapla"""
        self.v2g_power = sum(self.energy_flows.values())
        
        # Güç dengesi
        power_balance = self.total_generation + self.v2g_power - self.total_load
        
        # Frekans (güç dengesine duyarlı)
        freq_deviation = power_balance * 0.01
        noise = random.uniform(-0.05, 0.05)
        self.frequency = 50.0 + freq_deviation + noise
        
        # Voltaj
        voltage_deviation = power_balance * 0.1
        noise = random.uniform(-1, 1)
        self.voltage = 230.0 + voltage_deviation + noise
        
        # Geçmişe ekle
        self.freq_history.append(self.frequency)
        self.voltage_history.append(self.voltage)
        self.v2g_history.append(self.v2g_power)
    
    def detect_anomaly(self):
        """Anomali tespit"""
        self.total_checks += 1
        anomalies = []
        
        # Frekans kontrolü
        freq_dev = abs(self.frequency - 50.0)
        if freq_dev > 0.5:
            level = AlertLevel.WARNING if freq_dev < 1.0 else AlertLevel.CRITICAL
            anomalies.append({
                'type': 'FREQUENCY',
                'level': level,
                'value': f'{self.frequency:.2f} Hz',
                'message': f'Frekans sapması: {freq_dev:.2f} Hz'
            })
        
        # Voltaj kontrolü
        volt_dev = abs(self.voltage - 230.0)
        if volt_dev > 23:
            level = AlertLevel.WARNING if volt_dev < 30 else AlertLevel.CRITICAL
            anomalies.append({
                'type': 'VOLTAGE',
                'level': level,
                'value': f'{self.voltage:.1f} V',
                'message': f'Voltaj sapması: {volt_dev:.1f} V'
            })
        
        # Ani V2G değişimi
        if len(self.v2g_history) >= 3:
            recent = list(self.v2g_history)[-3:]
            change = max(recent) - min(recent)
            if change > 20:
                anomalies.append({
                    'type': 'RAPID_V2G',
                    'level': AlertLevel.WARNING,
                    'value': f'{change:.1f} kW',
                    'message': f'Ani V2G değişimi: {change:.1f} kW'
                })
        
        # Koordineli saldırı
        active_v2g = sum(1 for p in self.energy_flows.values() if p > 5)
        if active_v2g >= 3 and self.v2g_power > 30:
            anomalies.append({
                'type': 'COORDINATED',
                'level': AlertLevel.ATTACK,
                'value': f'{active_v2g} EV',
                'message': f'Koordineli V2G: {active_v2g} EV, {self.v2g_power:.1f} kW'
            })
            self.attack_detected = True
        
        # Aşırı V2G
        if self.v2g_power > 50:
            anomalies.append({
                'type': 'EXCESSIVE_V2G',
                'level': AlertLevel.CRITICAL,
                'value': f'{self.v2g_power:.1f} kW',
                'message': f'Aşırı V2G gücü!'
            })
        
        if anomalies:
            self.anomaly_count += 1
            self.alerts.extend(anomalies)
        
        return anomalies


def print_banner():
    """Başlık banner'ı"""
    print("\n" + "="*70)
    print("""
    ██╗   ██╗██████╗  ██████╗     ███████╗██╗███╗   ███╗
    ██║   ██║╚════██╗██╔════╝     ██╔════╝██║████╗ ████║
    ██║   ██║ █████╔╝██║  ███╗    ███████╗██║██╔████╔██║
    ╚██╗ ██╔╝██╔═══╝ ██║   ██║    ╚════██║██║██║╚██╔╝██║
     ╚████╔╝ ███████╗╚██████╔╝    ███████║██║██║ ╚═╝ ██║
      ╚═══╝  ╚══════╝ ╚═════╝     ╚══════╝╚═╝╚═╝     ╚═╝
                                                        
    V2G Protocol Manipulation Simulation
    Microgrid Destabilization Attack Demo
    """)
    print("="*70)


def print_grid_status(grid: MicrogridState, anomalies=None):
    """Şebeke durumunu yazdır"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Durum belirleme
    if grid.attack_detected:
        status = "🚨 SALDIRI TESPİT EDİLDİ"
        line_char = "🚨"
    elif any(a['level'] == AlertLevel.CRITICAL for a in (anomalies or [])):
        status = "⛔ KRİTİK"
        line_char = "⛔"
    elif any(a['level'] == AlertLevel.WARNING for a in (anomalies or [])):
        status = "⚠️ UYARI"
        line_char = "⚠️"
    else:
        status = "✅ NORMAL"
        line_char = "─"
    
    print(f"\n{line_char*35}")
    print(f"[{timestamp}] {status}")
    print(f"{line_char*35}")
    
    # Şebeke parametreleri
    freq_icon = "✅" if abs(grid.frequency - 50) < 0.5 else "⚠️"
    volt_icon = "✅" if abs(grid.voltage - 230) < 23 else "⚠️"
    
    print(f"\n📊 ŞEBEKE:")
    print(f"   {freq_icon} Frekans: {grid.frequency:.2f} Hz")
    print(f"   {volt_icon} Voltaj: {grid.voltage:.1f} V")
    print(f"   📈 Yük: {grid.total_load:.0f} kW | Üretim: {grid.total_generation:.0f} kW")
    print(f"   🔋 V2G: {grid.v2g_power:.1f} kW")
    
    # Bağlı EV'ler
    print(f"\n🚗 EV'ler ({len(grid.connected_evs)}):")
    for ev_id, info in grid.connected_evs.items():
        mode_icon = "⚡" if info['mode'] == 'v2g' else "🔌"
        print(f"   {mode_icon} {ev_id}: {info['power_kw']:.1f} kW ({info['mode']})")
    
    # Anomaliler
    if anomalies:
        print(f"\n🔔 ANOMALİLER:")
        for a in anomalies:
            icons = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️",
                AlertLevel.CRITICAL: "⛔",
                AlertLevel.ATTACK: "🚨"
            }
            print(f"   {icons.get(a['level'], '❓')} {a['message']}")
    
    # İstatistikler
    if grid.total_checks > 0:
        rate = (grid.anomaly_count / grid.total_checks) * 100
        print(f"\n📈 Kontrol: {grid.total_checks} | Anomali: {grid.anomaly_count} ({rate:.0f}%)")


async def normal_operation_phase(grid: MicrogridState, duration_sec=15):
    """Normal operasyon fazı"""
    print("\n" + "="*70)
    print("📗 FAZ 1: NORMAL OPERASYON")
    print("="*70)
    
    # Normal EV'ler ekle
    grid.add_ev("EV_001", mode='charging', power_kw=0)
    grid.add_ev("EV_002", mode='charging', power_kw=0)
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Normal şarj simülasyonu
        grid.update_v2g("EV_001", random.uniform(-11, -7))  # Negatif = şarj
        grid.update_v2g("EV_002", random.uniform(-22, -18))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


async def v2g_phase(grid: MicrogridState, duration_sec=15):
    """Normal V2G fazı"""
    print("\n" + "="*70)
    print("📘 FAZ 2: NORMAL V2G OPERASYONU")
    print("="*70)
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Normal V2G (düşük güç)
        grid.update_v2g("EV_001", random.uniform(3, 7))
        grid.update_v2g("EV_002", random.uniform(5, 10))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


async def attack_phase(grid: MicrogridState, duration_sec=20):
    """Saldırı fazı"""
    print("\n" + "🚨"*35)
    print("📕 FAZ 3: V2G PROTOCOL MANIPULATION SALDIRISI")
    print("🚨"*35)
    print("\n⚠️ Saldırgan sahte V2G komutları enjekte ediyor...")
    print("⚠️ Birden fazla 'sahte EV' koordineli deşarj başlatıyor...\n")
    
    # Saldırı: Birden fazla sahte EV ekle
    grid.add_ev("MALICIOUS_001", mode='v2g', power_kw=11)
    grid.add_ev("MALICIOUS_002", mode='v2g', power_kw=11)
    grid.add_ev("MALICIOUS_003", mode='v2g', power_kw=11)
    
    start = asyncio.get_event_loop().time()
    phase = 0
    
    while asyncio.get_event_loop().time() - start < duration_sec:
        phase += 1
        
        if phase % 3 == 0:
            # Osilasyon saldırısı
            print("\n💥 [SALDIRI] V2G Osilasyonu - Şebeke dengesizliği hedefleniyor!")
            for ev_id in grid.connected_evs:
                if "MALICIOUS" in ev_id:
                    power = 15 if phase % 6 == 0 else 0
                    grid.update_v2g(ev_id, power)
        else:
            # Koordineli yüksek güç
            for ev_id in grid.connected_evs:
                if "MALICIOUS" in ev_id:
                    grid.update_v2g(ev_id, random.uniform(10, 15))
        
        # Meşru EV'ler de etkileniyor
        grid.update_v2g("EV_001", random.uniform(8, 12))
        grid.update_v2g("EV_002", random.uniform(15, 22))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(2)


async def mitigation_phase(grid: MicrogridState, duration_sec=10):
    """Önlem fazı"""
    print("\n" + "="*70)
    print("📙 FAZ 4: MİTİGASYON - Saldırı Engelleniyor")
    print("="*70)
    print("\n🛡️ Anomali tespit sistemi devreye girdi!")
    print("🛡️ Kötü amaçlı EV'ler izole ediliyor...\n")
    
    # Kötü amaçlı EV'leri kaldır
    await asyncio.sleep(2)
    for ev_id in list(grid.connected_evs.keys()):
        if "MALICIOUS" in ev_id:
            print(f"   ⛔ {ev_id} bağlantısı kesiliyor...")
            del grid.connected_evs[ev_id]
            del grid.energy_flows[ev_id]
            await asyncio.sleep(1)
    
    grid.attack_detected = False
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Normal operasyona dön
        grid.update_v2g("EV_001", random.uniform(3, 6))
        grid.update_v2g("EV_002", random.uniform(5, 8))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


def print_summary(grid: MicrogridState):
    """Özet rapor"""
    print("\n" + "="*70)
    print("📊 SİMÜLASYON ÖZETİ")
    print("="*70)
    print(f"""
    Toplam Kontrol: {grid.total_checks}
    Tespit Edilen Anomali: {grid.anomaly_count}
    Anomali Oranı: {(grid.anomaly_count/grid.total_checks*100):.1f}%
    
    Saldırı Senaryosu: V2G Protocol Manipulation
    Hedef: Microgrid Destabilization
    
    Saldırı Yöntemleri:
    ├─ Sahte V2G Komut Enjeksiyonu
    ├─ Koordineli Multi-EV Deşarj
    └─ V2G Güç Osilasyonu
    
    Tespit Yöntemleri:
    ├─ Frekans/Voltaj İzleme
    ├─ Ani V2G Değişim Tespiti
    └─ Koordineli Saldırı Paterni Analizi
    """)
    print("="*70)


async def main():
    """Ana simülasyon"""
    print_banner()
    
    print("\n⏳ Simülasyon başlıyor...")
    print("   Bu demo 4 fazdan oluşur:")
    print("   1. Normal Operasyon (şarj)")
    print("   2. Normal V2G (araçtan şebekeye)")
    print("   3. SALDIRI (protokol manipülasyonu)")
    print("   4. Mitigasyon (saldırı engelleme)")
    print("\n   Ctrl+C ile durdurun.\n")
    
    await asyncio.sleep(3)
    
    grid = MicrogridState()
    
    try:
        # Faz 1: Normal operasyon
        await normal_operation_phase(grid, duration_sec=12)
        
        # Faz 2: Normal V2G
        await v2g_phase(grid, duration_sec=12)
        
        # Faz 3: Saldırı
        await attack_phase(grid, duration_sec=18)
        
        # Faz 4: Mitigasyon
        await mitigation_phase(grid, duration_sec=10)
        
        print_summary(grid)
        
    except KeyboardInterrupt:
        print("\n\n👋 Simülasyon durduruldu")
        print_summary(grid)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program sonlandırıldı")
