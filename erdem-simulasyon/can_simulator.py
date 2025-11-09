#!/usr/bin/env python3
"""
CAN-Bus Simülatörü - Elektrikli Araç İçin
Senaryo: "Hareket Halinde Şarj" Anomali Tespiti

3 Mod:
- normal: Araç park halinde, şarj oluyor (Normal)
- hareket: Araç hareket ediyor, şarj kapalı (Normal)
- anomali: Araç hareket ediyor AMA sahte "Park" verisi gönderiyor (ANOMALİ!)
"""

import asyncio
import time
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
        
        print(f"\n{'='*60}")
        print(f"🚗 CAN-Bus Simülatörü Başlatıldı")
        print(f"{'='*60}")
        print(f"Mod: {self.mod.upper()}")
        print(f"{'='*60}\n")
    
    def get_gercek_vites(self):
        """Aracın GERÇEK vites durumu"""
        if self.mod == "normal":
            return VitesKonumu.PARK
        elif self.mod in ["hareket", "anomali"]:
            return VitesKonumu.DRIVE
        return VitesKonumu.PARK
    
    def get_gercek_hiz(self):
        """Aracın GERÇEK hızı (km/h)"""
        if self.mod == "normal":
            return 0
        elif self.mod in ["hareket", "anomali"]:
            # Hafif varyasyon ekleyelim (gerçekçi olsun)
            import random
            return 30 + random.uniform(-2, 2)
        return 0
    
    def get_can_vites(self):
        """CAN-Bus'ta GÖRÜNEN vites (Saldırgan sahte veri gönderebilir)"""
        gercek_vites = self.get_gercek_vites()
        
        if self.mod == "anomali":
            # 🚨 SAHTECİLİK: Gerçekte "D" ama CAN'da "P" görünüyor!
            return VitesKonumu.PARK
        
        return gercek_vites
    
    def get_can_hiz(self):
        """CAN-Bus'ta GÖRÜNEN hız (Saldırgan sahte veri gönderebilir)"""
        gercek_hiz = self.get_gercek_hiz()
        
        if self.mod == "anomali":
            # 🚨 SAHTECİLİK: Gerçekte 30 km/h ama CAN'da 0 görünüyor!
            return 0
        
        return gercek_hiz
    
    def get_sarj_durumu(self):
        """Şarj aktif mi?"""
        if self.mod in ["normal", "anomali"]:
            return True  # Şarj aktif
        return False  # Hareket modunda şarj kapalı
    
    def print_can_message(self):
        """CAN mesajlarını konsola yazdır"""
        gercek_vites = self.get_gercek_vites()
        gercek_hiz = self.get_gercek_hiz()
        can_vites = self.get_can_vites()
        can_hiz = self.get_can_hiz()
        sarj_aktif = self.get_sarj_durumu()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Anomali var mı kontrol et
        anomali_var = (gercek_vites != can_vites) or (gercek_hiz != can_hiz)
        
        print(f"\n[{timestamp}] CAN-Bus Mesajları:")
        print(f"{'─'*60}")
        
        # Gerçek durum
        print(f"🔍 GERÇEK DURUM:")
        print(f"   ├─ Vites: {gercek_vites.value}")
        print(f"   └─ Hız: {gercek_hiz:.1f} km/h")
        
        # CAN-Bus'ta görünen
        print(f"\n📡 CAN-BUS'TA GÖRÜNEN:")
        vites_icon = "⚠️ " if can_vites != gercek_vites else "✅ "
        hiz_icon = "⚠️ " if abs(can_hiz - gercek_hiz) > 1 else "✅ "
        
        print(f"   ├─ {vites_icon}Vites (ID: 0x{self.CAN_ID_VITES:03X}): {can_vites.value}")
        print(f"   └─ {hiz_icon}Hız (ID: 0x{self.CAN_ID_HIZ:03X}): {can_hiz:.1f} km/h")
        
        # Şarj durumu
        print(f"\n🔋 ŞARJ DURUMU:")
        sarj_icon = "🔌" if sarj_aktif else "⏸️ "
        print(f"   └─ {sarj_icon}Şarj: {'AKTİF' if sarj_aktif else 'KAPALI'}")
        
        # Anomali uyarısı
        if anomali_var:
            print(f"\n{'🚨'*20}")
            print(f"⚠️  ANOMALİ TESPİT EDİLDİ!")
            print(f"    Sahte veri enjeksiyonu saldırısı olabilir!")
            print(f"{'🚨'*20}")
        
        print(f"{'─'*60}\n")
    
    async def run(self, interval=2):
        """CAN mesajlarını belirli aralıklarla üret"""
        self.running = True
        
        try:
            while self.running:
                self.print_can_message()
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
    
    if mod not in ["normal", "hareket", "anomali"]:
        print("❌ Geçersiz mod!")
        print("\nKullanım:")
        print("  python3 can_simulator.py [mod]")
        print("\nModlar:")
        print("  normal   - Araç park halinde, şarj oluyor (Normal durum)")
        print("  hareket  - Araç hareket ediyor, şarj kapalı (Normal durum)")
        print("  anomali  - Araç hareket ediyor + sahte CAN verisi (ANOMALİ!)")
        return
    
    simulator = CANSimulator(mod=mod)
    await simulator.run(interval=2)  # Her 2 saniyede bir mesaj

if __name__ == "__main__":
    asyncio.run(main())
