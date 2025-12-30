#!/usr/bin/env python3
"""
CAN-Bus Simülatörü - EVSE P-DoS Saldırısı Senaryosu
Senaryo: "Ödün Verilmiş EVSE Üzerinden CAN DoS Saldırısı"

3 Mod:
- normal: Araç park halinde, normal CAN trafiği (Normal)
- sarj: Araç şarj oluyor, normal CAN trafiği (Normal)
- dos_attack: EVSE ele geçirilmiş, 0x000 ID'li DoS saldırısı (KRİTİK ANOMALİ!)
"""

import asyncio
import time
import random
from datetime import datetime
from enum import Enum

class VitesKonumu(Enum):
    """Vites kutusu pozisyonları"""
    PARK = "P"
    REVERSE = "R"
    NEUTRAL = "N"
    DRIVE = "D"

class CANSimulator:
    def __init__(self, mod="normal"):
        self.mod = mod
        self.running = False
        
        # CAN Message IDs (Simüle)
        self.CAN_ID_VITES = 0x1F0  # Vites kutusu ECU
        self.CAN_ID_HIZ = 0x153    # Hız sensörü
        self.CAN_ID_BMS = 0x2A0    # Batarya Yönetim Sistemi
        self.CAN_ID_ABS = 0x1A0    # ABS denetleyicisi
        self.CAN_ID_ENGINE = 0x2B0 # Motor kontrolü
        
        # DoS Saldırı parametreleri
        self.CAN_ID_MALICIOUS = 0x000  # En yüksek öncelikli ID (saldırı için)
        self.dos_attack_active = False
        self.bus_load = 0  # CAN bus yükü %
        self.message_count = 0
        self.blocked_messages = 0
        
        print(f"\n{'='*70}")
        print(f"🚗 CAN-Bus Simülatörü Başlatıldı")
        print(f"{'='*70}")
        print(f"Mod: {self.mod.upper()}")
        if mod == "dos_attack":
            print(f"⚠️  UYARI: DoS Saldırısı Modu Aktif!")
            print(f"    EVSE ele geçirilmiş, kötü amaçlı bellenim yüklü!")
        print(f"{'='*70}\n")
    
    def get_sarj_durumu(self):
        """Şarj aktif mi?"""
        return self.mod in ["sarj", "dos_attack"]
    
    def simulate_normal_can_traffic(self):
        """Normal CAN veriyolu trafiğini simüle et"""
        messages = []
        
        # Normal ECU mesajları
        messages.append({
            'id': self.CAN_ID_VITES,
            'data': 'P',  # Park
            'priority': 'normal',
            'blocked': False
        })
        
        messages.append({
            'id': self.CAN_ID_HIZ,
            'data': '0 km/h',
            'priority': 'normal',
            'blocked': False
        })
        
        messages.append({
            'id': self.CAN_ID_BMS,
            'data': f'{random.randint(80, 95)}% SoC',
            'priority': 'normal',
            'blocked': False
        })
        
        messages.append({
            'id': self.CAN_ID_ABS,
            'data': 'OK',
            'priority': 'high',
            'blocked': False
        })
        
        messages.append({
            'id': self.CAN_ID_ENGINE,
            'data': 'Ready',
            'priority': 'high',
            'blocked': False
        })
        
        self.bus_load = random.randint(20, 40)  # Normal yük %20-40
        self.message_count = len(messages)
        self.blocked_messages = 0
        
        return messages
    
    def simulate_dos_attack(self):
        """DoS saldırısını simüle et - 0x000 ID ile arbitrasyon kilidi"""
        messages = []
        
        # SALDIRI: 0x000 ID'li mesaj seli
        for i in range(10):  # Yüksek frekanslı saldırı mesajları
            messages.append({
                'id': self.CAN_ID_MALICIOUS,
                'data': f'0x{"00" * 8}',  # Boş payload
                'priority': 'MAXIMUM',
                'blocked': False,
                'malicious': True
            })
        
        # Normal ECU'lar arbitrasyonu kaybediyor
        normal_ecus = [
            {'id': self.CAN_ID_VITES, 'data': 'P'},
            {'id': self.CAN_ID_HIZ, 'data': '0 km/h'},
            {'id': self.CAN_ID_BMS, 'data': '85% SoC'},
            {'id': self.CAN_ID_ABS, 'data': 'CRITICAL'},
            {'id': self.CAN_ID_ENGINE, 'data': 'ERROR'},
        ]
        
        for ecu in normal_ecus:
            messages.append({
                'id': ecu['id'],
                'data': ecu['data'],
                'priority': 'normal/high',
                'blocked': True,  # Arbitrasyonu kaybetti
                'malicious': False
            })
        
        self.dos_attack_active = True
        self.bus_load = 98  # Veriyolu %98 dolu
        self.message_count = len(messages)
        self.blocked_messages = len(normal_ecus)
        
        return messages
    
    def print_can_status(self):
        """CAN durumunu konsola yazdır"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        sarj_aktif = self.get_sarj_durumu()
        
        # Trafiği al
        if self.mod == "dos_attack":
            messages = self.simulate_dos_attack()
        else:
            messages = self.simulate_normal_can_traffic()
        
        print(f"\n[{timestamp}] CAN-Bus Durumu:")
        print(f"{'─'*70}")
        
        # Şarj durumu
        print(f"\n🔌 ŞARJ BAĞLANTISI:")
        sarj_icon = "🔋" if sarj_aktif else "⏸️ "
        print(f"   └─ {sarj_icon}Şarj: {'AKTİF (EVSE Bağlı)' if sarj_aktif else 'PASİF'}")
        
        # CAN Veriyolu İstatistikleri
        print(f"\n📊 CAN VERIYOLU İSTATİSTİKLERİ:")
        load_icon = "🚨" if self.bus_load > 80 else "✅ "
        print(f"   ├─ {load_icon}Bus Yükü: {self.bus_load}%")
        print(f"   ├─ Toplam Mesaj: {self.message_count}")
        print(f"   └─ Engellenen Mesaj: {self.blocked_messages}")
        
        # Mesaj Örnekleri
        print(f"\n📡 CAN MESAJLARI:")
        
        if self.mod == "dos_attack":
            # Kötü amaçlı mesajları göster
            malicious_count = sum(1 for m in messages if m.get('malicious', False))
            print(f"   🚨 SALDIRI TESPİT EDİLDİ!")
            print(f"   ├─ 0x000 ID'li mesajlar: {malicious_count} adet/saniye")
            print(f"   ├─ Arbitrasyon: KILITLENDI")
            print(f"   └─ ECU İletişimi: TAMAMEN ENGELLENEN")
            
            print(f"\n   ⛔ ENGELLENEN KRİTİK ECU'LAR:")
            for msg in messages:
                if not msg.get('malicious', False) and msg['blocked']:
                    print(f"      ├─ ID 0x{msg['id']:03X}: {msg['data']} [ARBITRASYON KAYBI]")
        
        else:
            # Normal mesajları göster
            print(f"   ✅ Normal CAN Trafiği")
            for msg in messages[:5]:  # İlk 5 mesaj
                print(f"   ├─ ID 0x{msg['id']:03X}: {msg['data']} [Öncelik: {msg['priority']}]")
        
        # Kritik Uyarı
        if self.dos_attack_active:
            print(f"\n{'🚨'*30}")
            print(f"⛔ KRİTİK P-DoS SALDIRISI DEVAM EDİYOR!")
            print(f"\n   Saldırı Tipi: Protocol-Compliant DoS")
            print(f"   Saldırı Vektörü: EVSE → CAN Bus (0x000 Priority Flood)")
            print(f"   Etki: TÜM ECU iletişimi kesildi")
            print(f"\n   Araç Durumu:")
            print(f"   ├─ Motor: ÇALIŞMIYOR (DTC: U0100)")
            print(f"   ├─ ABS: HATA (DTC: U0121)")
            print(f"   ├─ BMS: İLETİŞİM KAYBI (DTC: U0155)")
            print(f"   └─ Araç: HARD BRICK - Servis Gerekli!")
            print(f"\n   EVSE Kaynak:")
            print(f"   └─ Kötü amaçlı bellenim (rootkit) aktif")
            print(f"{'🚨'*30}")
        
        print(f"{'─'*70}\n")
    
    async def run(self, interval=2):
        """CAN durumunu belirli aralıklarla raporla"""
        self.running = True
        
        try:
            while self.running:
                self.print_can_status()
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 CAN Simülatörü kapatılıyor...")
            self.running = False

async def main():
    import sys
    
    # Komut satırından mod al
    mod = "normal"
    if len(sys.argv) > 1:
        mod = sys.argv[1].lower()
    
    if mod not in ["normal", "sarj", "dos_attack"]:
        print("❌ Geçersiz mod!")
        print("\nKullanım:")
        print("  python can_simulator.py [mod]")
        print("\nModlar:")
        print("  normal      - Araç park halinde, şarj YOK (Normal)")
        print("  sarj        - Araç şarj oluyor, normal CAN trafiği (Normal)")
        print("  dos_attack  - EVSE ele geçirilmiş, CAN DoS saldırısı (KRİTİK!)")
        print("\n⚠️  'dos_attack' modu, .md dosyasındaki P-DoS senaryosunu simüle eder!")
        return
    
    simulator = CANSimulator(mod=mod)
    await simulator.run(interval=2)  # Her 2 saniyede bir durum

if __name__ == "__main__":
    asyncio.run(main())
