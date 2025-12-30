#!/usr/bin/env python3
"""
Veri Toplayıcı ve Anomali Tespit Sistemi
Senaryo: "Hareket Halinde Şarj" Anomali Tespiti

Bu sistem 3 veri kaynağını birleştirir:
1. OCPP Verileri (Şarj durumu, enerji akışı)
2. CAN-Bus Verileri (Vites, hız - manipüle edilebilir)
3. GPS/Telematik Verileri (Gerçek konum, hız - güvenilir)

Anomali Tespit Mantığı:
- OCPP: Şarj Aktif + Enerji Akışı Var
- GPS: Araç Hareket Ediyor (Hız > 5 km/h)
→ Bu iki durum AYNI ANDA gerçekleşirse = ANOMALİ!
"""

import asyncio
import json
import subprocess
import re
from datetime import datetime
from collections import deque

class AnomalyDetector:
    def __init__(self):
        # Veri depoları (son 10 ölçüm)
        self.ocpp_data = deque(maxlen=10)
        self.can_data = deque(maxlen=10)
        self.gps_data = deque(maxlen=10)
        
        # Anomali sayacı
        self.anomaly_count = 0
        self.total_checks = 0
        
        # Eşik değerler
        self.SPEED_THRESHOLD = 5.0  # km/h - Bunun üstü "hareket"
        
        print(f"\n{'='*80}")
        print(f"🧠 ANOMALİ TESPİT SİSTEMİ BAŞLATILDI")
        print(f"{'='*80}")
        print(f"Eşik Değerler:")
        print(f"  └─ Hız Eşiği: {self.SPEED_THRESHOLD} km/h (Bunun üstü 'hareket')")
        print(f"{'='*80}\n")
    
    def parse_ocpp_output(self, output):
        """
        OCPP çıktısından şarj durumunu tespit et
        Örnek: ">>> YZ (AI) İÇİN GİRİŞ VERİSİ (OCPP): CP001 şarj oluyor, Değer: 1050"
        """
        try:
            if "şarj oluyor" in output or "Şarj Ediyor" in output.lower():
                # Enerji değerini çıkar
                match = re.search(r'Değer[:\s]+(\d+)', output)
                energy = int(match.group(1)) if match else 0
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'charging': True,
                    'energy': energy,
                    'source': 'OCPP'
                }
        except Exception as e:
            pass
        return None
    
    def parse_can_output(self, output):
        """
        CAN-Bus çıktısından vites ve hız bilgisini çıkar
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'CAN-Bus'
            }
            
            # Gerçek vites
            if "GERÇEK DURUM" in output:
                if "Vites: D" in output:
                    data['real_gear'] = 'D'
                elif "Vites: P" in output:
                    data['real_gear'] = 'P'
            
            # CAN'da görünen vites
            if "CAN-BUS'TA GÖRÜNEN" in output:
                if "Vites" in output:
                    match = re.search(r'Vites.*?:\s+([DP])', output)
                    if match:
                        data['can_gear'] = match.group(1)
            
            # Hız bilgisi
            match = re.search(r'Hız.*?:\s+([\d.]+)\s*km', output)
            if match:
                data['speed'] = float(match.group(1))
            
            # Anomali var mı CAN'da?
            if "ANOMALİ TESPİT EDİLDİ" in output and "CAN" in output:
                data['can_anomaly'] = True
            
            return data
        except Exception as e:
            pass
        return None
    
    def parse_gps_output(self, output):
        """
        GPS çıktısından konum ve hız bilgisini çıkar
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'GPS/Telematik'
            }
            
            # Hız
            match = re.search(r'Hız:\s+([\d.]+)\s*km/h', output)
            if match:
                data['speed'] = float(match.group(1))
            
            # Hareket durumu
            if "HAREKET HALİNDE" in output:
                data['moving'] = True
            elif "DURGUN" in output or "Park" in output:
                data['moving'] = False
            
            # Şarj bağlantısı
            if "Şarj Kablosu: BAĞLI" in output:
                data['cable_connected'] = True
            elif "BAĞLI DEĞİL" in output:
                data['cable_connected'] = False
            
            # GPS koordinatları
            lat_match = re.search(r'Enlem.*?:\s+([\d.]+)', output)
            lon_match = re.search(r'Boylam.*?:\s+([\d.]+)', output)
            if lat_match and lon_match:
                data['latitude'] = float(lat_match.group(1))
                data['longitude'] = float(lon_match.group(1))
            
            return data
        except Exception as e:
            pass
        return None
    
    def detect_anomaly(self):
        """
        Ana anomali tespit mantığı:
        1. OCPP'den: Şarj aktif mi?
        2. GPS'ten: Araç hareket ediyor mu?
        3. İkisi de DOĞRU ise → ANOMALİ!
        """
        self.total_checks += 1
        
        # Son verileri al
        latest_ocpp = self.ocpp_data[-1] if self.ocpp_data else None
        latest_gps = self.gps_data[-1] if self.gps_data else None
        latest_can = self.can_data[-1] if self.can_data else None
        
        if not latest_ocpp or not latest_gps:
            return None
        
        # Anomali kontrolü
        charging = latest_ocpp.get('charging', False)
        gps_speed = latest_gps.get('speed', 0)
        moving = gps_speed > self.SPEED_THRESHOLD
        
        is_anomaly = charging and moving
        
        if is_anomaly:
            self.anomaly_count += 1
        
        # Detaylı rapor
        result = {
            'timestamp': datetime.now().isoformat(),
            'check_number': self.total_checks,
            'anomaly_detected': is_anomaly,
            'ocpp': {
                'charging': charging,
                'energy': latest_ocpp.get('energy', 0)
            },
            'gps': {
                'speed': gps_speed,
                'moving': moving,
                'latitude': latest_gps.get('latitude'),
                'longitude': latest_gps.get('longitude')
            },
            'can': latest_can if latest_can else None
        }
        
        return result
    
    def print_analysis(self, result):
        """Analiz sonucunu konsola yazdır"""
        if not result:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"[{timestamp}] 🧠 ANOMALİ ANALİZİ #{result['check_number']}")
        print(f"{'='*80}")
        
        # OCPP Durumu
        print(f"\n📊 OCPP VERİLERİ (Şarj İstasyonu):")
        ocpp = result['ocpp']
        charging_icon = "🔋" if ocpp['charging'] else "⏸️ "
        print(f"   ├─ {charging_icon}Şarj Durumu: {'AKTİF' if ocpp['charging'] else 'PASİF'}")
        print(f"   └─ Enerji Akışı: {ocpp['energy']} Wh")
        
        # GPS Durumu
        print(f"\n📍 GPS/TELEMATİK VERİLERİ (Güvenilir Kaynak):")
        gps = result['gps']
        moving_icon = "🏃" if gps['moving'] else "🅿️ "
        print(f"   ├─ {moving_icon}Hareket Durumu: {'HAREKET HALİNDE' if gps['moving'] else 'DURGUN'}")
        print(f"   ├─ Hız: {gps['speed']:.1f} km/h")
        if gps['latitude'] and gps['longitude']:
            print(f"   └─ Konum: {gps['latitude']:.6f}, {gps['longitude']:.6f}")
        
        # CAN Durumu (varsa)
        if result['can']:
            print(f"\n🚗 CAN-BUS VERİLERİ (Manipüle Edilebilir):")
            can = result['can']
            if 'real_gear' in can:
                print(f"   ├─ Gerçek Vites: {can['real_gear']}")
            if 'can_gear' in can:
                gear_icon = "⚠️ " if can.get('real_gear') != can.get('can_gear') else "✅ "
                print(f"   ├─ {gear_icon}CAN'da Görünen Vites: {can['can_gear']}")
            if 'can_anomaly' in can:
                print(f"   └─ 🚨 CAN-Bus'ta sahte veri tespit edildi!")
        
        # Anomali Kararı
        print(f"\n{'─'*80}")
        print(f"🎯 KARAR:")
        
        if result['anomaly_detected']:
            print(f"\n{'🚨'*30}")
            print(f"⛔ KRİTİK ANOMALİ TESPİT EDİLDİ!")
            print(f"\n   Tespit Edilen Durum:")
            print(f"   ├─ OCPP: Şarj AKTİF ✓")
            print(f"   ├─ GPS: Araç HAREKET EDİYOR ✓ ({gps['speed']:.1f} km/h)")
            print(f"   └─ Sonuç: HAREKET HALİNDE ŞARJ = GÜVENLİK İHLALİ!")
            print(f"\n   Olası Senaryo:")
            print(f"   └─ CAN-Bus sahte veri enjeksiyonu saldırısı")
            print(f"      BMS'i kandırarak şarjın kesilmesini engelliyor!")
            print(f"\n   Önerilen Aksiyon:")
            print(f"   ├─ OCPP: RemoteStopTransaction gönder")
            print(f"   ├─ Fiziksel: Şarj istasyonunu acil durdur")
            print(f"   └─ Güvenlik: Olayı loglayıp araştır")
            print(f"{'🚨'*30}")
        else:
            print(f"   ✅ NORMAL - Anomali tespit edilmedi")
            print(f"   └─ Sistem güvenli durumda")
        
        # İstatistikler
        print(f"\n📈 İSTATİSTİKLER:")
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"   ├─ Toplam Kontrol: {self.total_checks}")
        print(f"   ├─ Anomali Sayısı: {self.anomaly_count}")
        print(f"   └─ Anomali Oranı: {anomaly_rate:.1f}%")
        
        print(f"{'='*80}\n")
    
    async def monitor(self, interval=3):
        """
        Belirli aralıklarla simüle veri topla ve analiz et
        (Gerçek uygulamada WebSocket veya API'den veri gelir)
        """
        print("🔍 İzleme başlatılıyor...")
        print("ℹ️  Not: Bu basit versiyon simüle veri kullanıyor.")
        print("    Gerçek uygulamada OCPP/CAN/GPS'ten canlı veri gelir.\n")
        
        # Simüle veri örnekleri
        scenarios = [
            {
                'name': 'Normal Park Şarjı',
                'ocpp': {'charging': True, 'energy': 1500},
                'gps': {'speed': 0.8, 'moving': False, 'latitude': 41.0082, 'longitude': 28.9784},
                'can': {'real_gear': 'P', 'can_gear': 'P', 'speed': 0}
            },
            {
                'name': 'Normal Sürüş',
                'ocpp': {'charging': False, 'energy': 0},
                'gps': {'speed': 35.2, 'moving': True, 'latitude': 41.0092, 'longitude': 28.9794},
                'can': {'real_gear': 'D', 'can_gear': 'D', 'speed': 35}
            },
            {
                'name': '🚨 ANOMALİ: Hareket Halinde Şarj',
                'ocpp': {'charging': True, 'energy': 2000},
                'gps': {'speed': 30.5, 'moving': True, 'latitude': 41.0102, 'longitude': 28.9804},
                'can': {'real_gear': 'D', 'can_gear': 'P', 'speed': 0, 'can_anomaly': True}
            }
        ]
        
        try:
            scenario_index = 0
            while True:
                # Simüle veri al
                scenario = scenarios[scenario_index % len(scenarios)]
                
                print(f"\n{'─'*80}")
                print(f"📥 Senaryo: {scenario['name']}")
                print(f"{'─'*80}")
                
                # Verileri ekle
                self.ocpp_data.append({
                    'timestamp': datetime.now().isoformat(),
                    'source': 'OCPP',
                    **scenario['ocpp']
                })
                
                self.gps_data.append({
                    'timestamp': datetime.now().isoformat(),
                    'source': 'GPS/Telematik',
                    **scenario['gps']
                })
                
                if scenario['can']:
                    self.can_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'source': 'CAN-Bus',
                        **scenario['can']
                    })
                
                # Anomali tespit et
                result = self.detect_anomaly()
                if result:
                    self.print_analysis(result)
                
                scenario_index += 1
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 İzleme durduruldu")
            print(f"\n📊 ÖZET:")
            print(f"   ├─ Toplam Kontrol: {self.total_checks}")
            print(f"   ├─ Tespit Edilen Anomali: {self.anomaly_count}")
            anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
            print(f"   └─ Başarı Oranı: {anomaly_rate:.1f}%\n")

async def main():
    detector = AnomalyDetector()
    await detector.monitor(interval=5)  # Her 5 saniyede bir analiz

if __name__ == "__main__":
    asyncio.run(main())
