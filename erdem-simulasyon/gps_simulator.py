#!/usr/bin/env python3
"""
GPS/Telematik Simülatörü - Elektrikli Araç İçin
Senaryo: "Hareket Halinde Şarj" Anomali Tespiti

Aracın gerçek GPS konumunu ve hızını simüle eder.
Bu veri MANIPÜLE EDİLEMEZ çünkü harici sunucudan gelir.

3 Mod:
- durgun: Araç sabit konumda (Park halinde şarj)
- hareket: Araç hareket ediyor (Normal sürüş)
- anomali: Araç hareket ediyor (Şarj sırasında hareket - ANOMALİ!)
"""

import asyncio
import math
from datetime import datetime
from enum import Enum

class GPSSimulator:
    def __init__(self, mod="durgun"):
        self.mod = mod
        self.running = False
        
        # Başlangıç konumu: İstanbul, Türkiye (Şarj İstasyonu)
        self.base_lat = 41.0082  # Enlem
        self.base_lon = 28.9784  # Boylam
        
        # Mevcut konum
        self.current_lat = self.base_lat
        self.current_lon = self.base_lon
        
        # Önceki konum (hız hesabı için)
        self.prev_lat = self.base_lat
        self.prev_lon = self.base_lon
        
        # Hareket parametreleri
        self.direction = 0  # Derece (0=Kuzey, 90=Doğu)
        self.step_count = 0
        
        print(f"\n{'='*70}")
        print(f"📡 GPS/Telematik Simülatörü Başlatıldı")
        print(f"{'='*70}")
        print(f"Mod: {self.mod.upper()}")
        print(f"Başlangıç Konumu: {self.base_lat:.6f}, {self.base_lon:.6f}")
        print(f"{'='*70}\n")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        İki GPS koordinatı arasındaki mesafeyi hesapla (metre)
        Haversine formülü kullanılıyor
        """
        R = 6371000  # Dünya yarıçapı (metre)
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_speed(self, interval):
        """
        Önceki konumdan bu yana geçen sürede hızı hesapla (km/h)
        """
        distance = self.calculate_distance(
            self.prev_lat, self.prev_lon,
            self.current_lat, self.current_lon
        )
        
        # Metre/saniye → km/saat
        speed_ms = distance / interval
        speed_kmh = speed_ms * 3.6
        
        return speed_kmh
    
    def update_position(self):
        """
        Konumu güncelle (mod'a göre)
        """
        self.prev_lat = self.current_lat
        self.prev_lon = self.current_lon
        
        if self.mod == "durgun":
            # Sabit kal (hafif GPS drift simülasyonu)
            import random
            self.current_lat = self.base_lat + random.uniform(-0.00001, 0.00001)
            self.current_lon = self.base_lon + random.uniform(-0.00001, 0.00001)
        
        elif self.mod in ["hareket", "anomali"]:
            # Hareket simülasyonu: Kuzey-doğu yönünde ilerle
            # Yaklaşık 30 km/h hız için (2 saniye aralıkla ~16.7 metre)
            
            self.step_count += 1
            
            # Basit rota: Kuzey-doğu yönünde zigzag
            if self.step_count % 10 < 5:
                self.direction = 45  # Kuzey-doğu
            else:
                self.direction = 90  # Doğu
            
            # 16.7 metre hareket (30 km/h için)
            distance_km = 0.0167  # km
            
            # Yeni koordinatları hesapla
            lat_change = distance_km * math.cos(math.radians(self.direction)) / 111.32
            lon_change = distance_km * math.sin(math.radians(self.direction)) / (111.32 * math.cos(math.radians(self.current_lat)))
            
            self.current_lat += lat_change
            self.current_lon += lon_change
    
    def get_hareket_durumu(self):
        """Araç hareket ediyor mu?"""
        if self.mod == "durgun":
            return False
        elif self.mod in ["hareket", "anomali"]:
            return True
        return False
    
    def get_sarj_durumu(self):
        """Şarj aktif mi? (OCPP'den gelmeli ama simülasyon için)"""
        if self.mod in ["durgun", "anomali"]:
            return True  # Şarj aktif
        return False  # Hareket modunda şarj kapalı
    
    def print_telematic_data(self, interval):
        """GPS ve telematik verilerini konsola yazdır"""
        self.update_position()
        
        speed = self.calculate_speed(interval)
        hareket_ediyor = self.get_hareket_durumu()
        sarj_aktif = self.get_sarj_durumu()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Anomali kontrolü: Şarj aktif VE hareket ediyor
        anomali_var = sarj_aktif and hareket_ediyor
        
        print(f"\n[{timestamp}] GPS/Telematik Verileri:")
        print(f"{'─'*70}")
        
        # GPS Koordinatları
        print(f"📍 GPS KONUM:")
        print(f"   ├─ Enlem (Latitude):  {self.current_lat:.6f}°")
        print(f"   ├─ Boylam (Longitude): {self.current_lon:.6f}°")
        print(f"   └─ Yön: {self.direction}° ({self._get_direction_text()})")
        
        # Hız ve Hareket
        print(f"\n🚗 HAREKET VERİLERİ:")
        hareket_icon = "🏃" if hareket_ediyor else "🅿️ "
        print(f"   ├─ {hareket_icon}Hız: {speed:.1f} km/h")
        print(f"   └─ Durum: {'HAREKET HALİNDE' if hareket_ediyor else 'DURGUN (Park)'}")
        
        # Şarj durumu (Telematik üzerinden bildiriliyor)
        print(f"\n🔌 ŞARJ BAĞLANTISI:")
        sarj_icon = "🔋" if sarj_aktif else "❌"
        print(f"   └─ {sarj_icon}Şarj Kablosu: {'BAĞLI' if sarj_aktif else 'BAĞLI DEĞİL'}")
        
        # Hücresel bağlantı (Telematik ünitesi)
        print(f"\n📶 TELEMATIK:")
        print(f"   ├─ Bağlantı: 4G LTE")
        print(f"   ├─ Sinyal Gücü: -75 dBm (İyi)")
        print(f"   └─ Sunucu: CSMS (Bağlı)")
        
        # Anomali uyarısı
        if anomali_var:
            print(f"\n{'🚨'*25}")
            print(f"⚠️  KRİTİK ANOMALİ TESPİT EDİLDİ!")
            print(f"    GPS: Araç hareket ediyor ({speed:.1f} km/h)")
            print(f"    Telematik: Şarj kablosu hala bağlı!")
            print(f"    → Hareket halinde şarj = GÜVENLİK İHLALİ!")
            print(f"{'🚨'*25}")
        
        # Güvenlik durumu
        print(f"\n🛡️  GÜVENLİK DURUMU:")
        if anomali_var:
            print(f"   └─ ❌ ANORMAL - Acil müdahale gerekli!")
        else:
            print(f"   └─ ✅ NORMAL")
        
        print(f"{'─'*70}\n")
    
    def _get_direction_text(self):
        """Yönü metne çevir"""
        if self.direction < 22.5 or self.direction >= 337.5:
            return "Kuzey"
        elif 22.5 <= self.direction < 67.5:
            return "Kuzey-Doğu"
        elif 67.5 <= self.direction < 112.5:
            return "Doğu"
        elif 112.5 <= self.direction < 157.5:
            return "Güney-Doğu"
        elif 157.5 <= self.direction < 202.5:
            return "Güney"
        elif 202.5 <= self.direction < 247.5:
            return "Güney-Batı"
        elif 247.5 <= self.direction < 292.5:
            return "Batı"
        else:
            return "Kuzey-Batı"
    
    async def run(self, interval=2):
        """GPS verilerini belirli aralıklarla üret"""
        self.running = True
        
        try:
            while self.running:
                self.print_telematic_data(interval)
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 GPS Simülatörü kapatılıyor...")
            self.running = False

async def main():
    import sys
    
    # Komut satırından mod al
    mod = "durgun"
    if len(sys.argv) > 1:
        mod = sys.argv[1].lower()
    
    if mod not in ["durgun", "hareket", "anomali"]:
        print("❌ Geçersiz mod!")
        print("\nKullanım:")
        print("  python3 gps_simulator.py [mod]")
        print("\nModlar:")
        print("  durgun   - Araç sabit konumda (Park halinde şarj - Normal)")
        print("  hareket  - Araç hareket ediyor (Normal sürüş, şarj kapalı)")
        print("  anomali  - Araç hareket ediyor + şarj aktif (ANOMALİ!)")
        return
    
    simulator = GPSSimulator(mod=mod)
    await simulator.run(interval=2)  # Her 2 saniyede bir veri

if __name__ == "__main__":
    asyncio.run(main())
