#!/usr/bin/env python3
"""
Canlı Veri Toplayıcı ve Anomali Tespit Sistemi
Gerçek zamanlı log dosyalarından veri okur ve anomali tespit eder.

Kullanım:
1. Simülatörleri log dosyasına yönlendirerek çalıştırın
2. Bu scripti çalıştırın
3. Gerçek zamanlı anomali tespiti görün
"""

import asyncio
import re
import os
from datetime import datetime
from collections import deque

class LiveAnomalyDetector:
    def __init__(self):
        # Log dosya yolları
        self.GPS_LOG = "gps_log.txt"
        self.CAN_LOG = "can_log.txt"
        self.CSMS_LOG = "csms_log.txt"
        
        # Son okunan satır numaraları
        self.gps_last_line = 0
        self.can_last_line = 0
        self.csms_last_line = 0
        
        # Veri depoları
        self.ocpp_charging = False
        self.ocpp_energy = 0
        
        self.gps_speed = 0.0
        self.gps_moving = False
        self.gps_lat = None
        self.gps_lon = None
        
        self.can_real_gear = None
        self.can_shown_gear = None
        self.can_anomaly = False
        
        # İstatistikler
        self.anomaly_count = 0
        self.total_checks = 0
        
        # Eşik değer
        self.SPEED_THRESHOLD = 5.0
        
        print(f"\n{'='*80}")
        print(f"🔴 CANLI ANOMALİ TESPİT SİSTEMİ BAŞLATILDI")
        print(f"{'='*80}")
        print(f"Log Dosyaları:")
        print(f"  ├─ GPS: {self.GPS_LOG}")
        print(f"  ├─ CAN: {self.CAN_LOG}")
        print(f"  └─ CSMS: {self.CSMS_LOG}")
        print(f"\nEşik Değer:")
        print(f"  └─ Hız: {self.SPEED_THRESHOLD} km/h (Üstü 'hareket')")
        print(f"{'='*80}\n")
    
    def read_new_lines(self, filepath, last_line):
        """Dosyadan yeni satırları oku"""
        try:
            if not os.path.exists(filepath):
                return [], last_line
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                new_lines = lines[last_line:]
                return new_lines, len(lines)
        except Exception as e:
            return [], last_line
    
    def parse_gps_data(self, lines):
        """GPS log'undan veri çıkar"""
        text = ''.join(lines)
        
        # Hız
        match = re.search(r'Hız:\s+([\d.]+)\s*km/h', text)
        if match:
            self.gps_speed = float(match.group(1))
        
        # Hareket durumu
        if "HAREKET HALİNDE" in text:
            self.gps_moving = True
        elif "DURGUN" in text or "Park" in text:
            self.gps_moving = False
        
        # Koordinatlar
        lat_match = re.search(r'Enlem.*?:\s+([\d.]+)', text)
        lon_match = re.search(r'Boylam.*?:\s+([\d.]+)', text)
        if lat_match and lon_match:
            self.gps_lat = float(lat_match.group(1))
            self.gps_lon = float(lon_match.group(1))
    
    def parse_can_data(self, lines):
        """CAN log'undan veri çıkar"""
        text = ''.join(lines)
        
        # Gerçek vites
        if "GERÇEK DURUM" in text:
            if "Vites: D" in text:
                self.can_real_gear = 'D'
            elif "Vites: P" in text:
                self.can_real_gear = 'P'
        
        # CAN'da görünen vites
        match = re.search(r'CAN-BUS.*?Vites.*?:\s+([DP])', text, re.DOTALL)
        if match:
            self.can_shown_gear = match.group(1)
        
        # Anomali var mı?
        self.can_anomaly = "ANOMALİ TESPİT EDİLDİ" in text
    
    def parse_csms_data(self, lines):
        """CSMS log'undan OCPP verisi çıkar"""
        text = ''.join(lines)
        
        # Şarj durumu
        if "şarj oluyor" in text.lower() or "metervalues" in text.lower():
            self.ocpp_charging = True
            
            # Enerji değeri
            match = re.search(r'Değer[:\s]+(\d+)', text)
            if match:
                self.ocpp_energy = int(match.group(1))
        
        # Bağlantı kesildi mi?
        if "bağlantıyı kapattı" in text.lower() or "connection closed" in text.lower():
            self.ocpp_charging = False
            self.ocpp_energy = 0
    
    def detect_anomaly(self):
        """Ana anomali tespit mantığı"""
        self.total_checks += 1
        
        # GPS'e göre hareket kontrolü
        moving = self.gps_speed > self.SPEED_THRESHOLD
        
        # Anomali: Şarj aktif VE araç hareket ediyor
        is_anomaly = self.ocpp_charging and moving
        
        if is_anomaly:
            self.anomaly_count += 1
        
        return is_anomaly
    
    def print_status(self, is_anomaly):
        """Mevcut durumu ve anomali sonucunu yazdır"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"[{timestamp}] 🧠 CANLI ANALİZ #{self.total_checks}")
        print(f"{'='*80}")
        
        # OCPP Durumu
        print(f"\n📊 OCPP VERİLERİ (CSMS'ten):")
        charging_icon = "🔋" if self.ocpp_charging else "⏸️ "
        print(f"   ├─ {charging_icon}Şarj Durumu: {'AKTİF' if self.ocpp_charging else 'PASİF'}")
        print(f"   └─ Enerji: {self.ocpp_energy} Wh")
        
        # GPS Durumu
        print(f"\n📍 GPS/TELEMATİK VERİLERİ:")
        moving_icon = "🏃" if self.gps_speed > self.SPEED_THRESHOLD else "🅿️ "
        print(f"   ├─ {moving_icon}Durum: {'HAREKET HALİNDE' if self.gps_moving else 'DURGUN'}")
        print(f"   ├─ Hız: {self.gps_speed:.1f} km/h")
        if self.gps_lat and self.gps_lon:
            print(f"   └─ Konum: {self.gps_lat:.6f}, {self.gps_lon:.6f}")
        
        # CAN Durumu
        print(f"\n🚗 CAN-BUS VERİLERİ:")
        if self.can_real_gear:
            print(f"   ├─ Gerçek Vites: {self.can_real_gear}")
        if self.can_shown_gear:
            gear_match = self.can_real_gear == self.can_shown_gear
            gear_icon = "✅ " if gear_match else "⚠️ "
            print(f"   ├─ {gear_icon}CAN'da Görünen: {self.can_shown_gear}")
        if self.can_anomaly:
            print(f"   └─ 🚨 CAN'da sahte veri tespit edildi!")
        
        # Anomali Kararı
        print(f"\n{'─'*80}")
        print(f"🎯 KARAR:")
        
        if is_anomaly:
            print(f"\n{'🚨'*30}")
            print(f"⛔ KRİTİK ANOMALİ TESPİT EDİLDİ!")
            print(f"\n   Tespit Edilen Durum:")
            print(f"   ├─ OCPP: Şarj AKTİF ✓")
            print(f"   ├─ GPS: Araç HAREKET EDİYOR ✓ ({self.gps_speed:.1f} km/h)")
            print(f"   └─ Sonuç: HAREKET HALİNDE ŞARJ = GÜVENLİK İHLALİ!")
            
            if self.can_anomaly:
                print(f"\n   Ek Kanıt:")
                print(f"   └─ CAN-Bus'ta sahte veri enjeksiyonu tespit edildi!")
            
            print(f"\n   Önerilen Aksiyon:")
            print(f"   ├─ OCPP: RemoteStopTransaction gönder")
            print(f"   ├─ Fiziksel: Şarj istasyonunu acil durdur")
            print(f"   └─ Güvenlik: Olayı kaydet ve araştır")
            print(f"{'🚨'*30}")
        else:
            print(f"   ✅ NORMAL - Anomali tespit edilmedi")
            if not self.ocpp_charging:
                print(f"   └─ Şarj aktif değil")
            elif self.gps_speed <= self.SPEED_THRESHOLD:
                print(f"   └─ Araç durgun ({self.gps_speed:.1f} km/h)")
        
        # İstatistikler
        print(f"\n📈 İSTATİSTİKLER:")
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"   ├─ Toplam Kontrol: {self.total_checks}")
        print(f"   ├─ Tespit Edilen Anomali: {self.anomaly_count}")
        print(f"   └─ Anomali Oranı: {anomaly_rate:.1f}%")
        
        print(f"{'='*80}\n")
    
    async def monitor(self, interval=3):
        """Log dosyalarını sürekli izle ve analiz et"""
        print("🔍 Log dosyaları izleniyor...")
        print("ℹ️  Simülatörlerin çalıştığından emin olun!\n")
        
        try:
            while True:
                # Yeni satırları oku
                gps_lines, self.gps_last_line = self.read_new_lines(self.GPS_LOG, self.gps_last_line)
                can_lines, self.can_last_line = self.read_new_lines(self.CAN_LOG, self.can_last_line)
                csms_lines, self.csms_last_line = self.read_new_lines(self.CSMS_LOG, self.csms_last_line)
                
                # Verileri parse et
                if gps_lines:
                    self.parse_gps_data(gps_lines)
                if can_lines:
                    self.parse_can_data(can_lines)
                if csms_lines:
                    self.parse_csms_data(csms_lines)
                
                # Anomali tespit et ve göster
                is_anomaly = self.detect_anomaly()
                self.print_status(is_anomaly)
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 İzleme durduruldu")
            print(f"\n📊 ÖZET:")
            print(f"   ├─ Toplam Kontrol: {self.total_checks}")
            print(f"   ├─ Tespit Edilen Anomali: {self.anomaly_count}")
            anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
            print(f"   └─ Anomali Oranı: {anomaly_rate:.1f}%\n")

async def main():
    detector = LiveAnomalyDetector()
    await detector.monitor(interval=3)  # Her 3 saniyede bir kontrol

if __name__ == "__main__":
    asyncio.run(main())
