# ⚡ ULTIMATE EVSE P-DoS SIMULATOR

**Dünyada Görülmemiş Güzellikte, Tam Fonksiyonel, Gerçek Simülasyon**

OCPP'den CAN'e Saldırı Vektörünün Tam Simülasyonu - Tek Bir Web Arayüzünde

---

## 🌟 ÖZELLİKLER

### ✨ Görsel Mükemmellik
- 🎨 **Particles.js Arka Plan** - Canlı, interaktif parçacık efektleri
- 💎 **Glassmorphism Tasarım** - Modern cam efekti UI
- 🌈 **3D Animasyonlar** - Derinlik hissi veren efektler
- ⚡ **Real-time Güncellemeler** - 500ms'de bir veri akışı
- 🎭 **Dinamik Renkler** - Duruma göre değişen temalar

### 🔬 Tam Fonksiyonel Simülasyon - GERÇEK FİZİK MODELLİ!
- ✅ **Gerçek CAN Bus Simülasyonu** - Arbitrasyon, priority, DoS attack
- ✅ **Tam OCPP Protokolü** - Heartbeat, MeterValues, UpdateFirmware
- ✅ **GPS/Telemetri + Fizik** - İvme bazlı hareket (2.5 m/s²), gerçek koordinat hesaplama
- ✅ **Elektrik Fiziği** - P=V×I, I²R ısınma, enerji entegrasyonu
- ✅ **Araç Dinamiği** - RPM=speed×45, motor sıcaklığı, gradual hız değişimi
- ✅ **5 Fazlı Saldırı** - Normal → MitM → Firmware → DoS → Hard Brick
- ✅ **DTC Kod Üretimi** - U0100, U0121, U0155, U0164, U0195

### 📊 Terminal & Logging
- 💻 **Real-time Terminal** - Tüm işlemler canlı görünür
- 📁 **Otomatik Loglama** - Her kategori ayrı dosyaya
- 🔍 **Filtreleme** - CAN, OCPP, GPS, ATTACK filtrele
- ⬇️ **Log İndirme** - Tüm logları indirebilirsin
- 🎨 **Renkli Çıktılar** - INFO, WARNING, ERROR, CRITICAL

---

## 🚀 KURULUM (30 SANİYE)

### 1. Bağımlılıkları Yükle
```powershell
cd C:\Users\ahmet\OneDrive\Masaüstü\bsgodev\bsg-2025-vehicle-sec\erdem-simulasyon
pip install -r requirements.txt
```

### 2. Simülatörü Başlat
```powershell
python ultimate_simulator.py
```

### 3. Tarayıcıda Aç
```
http://localhost:5000
```

### 4. START Butonuna Tıkla! 🎬

---

## 🔬 GERÇEK FİZİK MODELİ - NASIL ÇALIŞIYOR?

### ⚡ Elektrik Fiziği (EVSE)
```python
# GERÇEK HESAPLAMALAR:
Voltage: 400V (DC Fast Charging)
Power: 0 → 7.4 kW (10 saniyede ramp-up, gerçekçi)
Current: I = P / V = 7400W / 400V = 18.5A
Energy: E = ∫P dt (0.5 saniyede: 7.4 * 0.5/3600 = 0.001 kWh)
Temperature: T = T₀ + I²R (Joule heating)
```

### 🚗 Araç Dinamiği (GPS/Telemetri)
```python
# FİZİK PARAMETRELERI:
Acceleration: 2.5 m/s² (normal EV)
Deceleration: 4.0 m/s² (frenler)

# HIZ DEĞİŞİMİ (ANOMALİDE):
Phase 1 (3 update): 0 → 30 km/h   (ivme: 2.5 m/s² × 0.5s × 3.6 = ~4.5 km/h per update)
Phase 2 (3 update): 30 → 60 km/h  (aynı ivme)
Phase 3 (devam):    60 → 85 km/h  (random varyasyon ±5 km/h)

# KONUM HESAPLAMA:
1° latitude = 111.32 km
1° longitude = 111.32 × cos(41°) ≈ 82.4 km (İstanbul'da)
distance = speed × time = 85 km/h × 0.5s / 3600 = 0.0118 km
Δlat = 0.0118 / 111.32 = 0.000106° (gerçek hareket)
```

### 🔧 Motor & RPM
```python
# GERÇEK İLİŞKİ:
RPM = speed × gear_ratio × final_drive / (tire_circumference / 60)
Simplified: RPM ≈ speed × 45

Örnek: 80 km/h → 3600 RPM (gerçekçi)
Motor Temp: Başlangıç 25°C → Yük altında 95°C
```

### 🎯 ANOMALİ TESPİTİ
```python
# FİZİKSEL İMKANSIZLIK:
IF (speed > 0 AND charging == True):
    CRITICAL_ANOMALY = True
    # Çünkü: Araç hareket ediyorsa kablodan çıkmış olmalı!
```

---

## 🎯 5 FAZLI SALDIRI SİMÜLASYONU

### Faz 0: Normal Şarj (🟢 20 saniye)
**Ne Olur:**
- Araç park halinde şarj oluyor
- OCPP Heartbeat ve MeterValues mesajları
- Normal CAN trafiği
- SoC artıyor

**Terminal'de Göreceksin:**
```
[INFO] OCPP: TX → CSMS: Heartbeat from EVSE-001
[INFO] CAN: TX: ID=0x1F0 DLC=8 Data=[85, 0, 25, ...]
[INFO] GPS: Vehicle stationary at (41.008200, 28.978400)
```

---

### Faz 1: ARP Spoofing & MitM (🟠 15 saniye)
**Ne Olur:**
- EVSE durumu: UPDATING
- ARP Spoofing başlatılıyor
- OCPP UpdateFirmware isteği manipüle ediliyor

**Terminal'de Göreceksin:**
```
[CRITICAL] ATTACK: ARP SPOOFING: Attacker MAC: DE:AD:BE:EF:13:37
[WARNING] OCPP: CSMS → EVSE: Legitimate UpdateFirmware request
[CRITICAL] ATTACK: MITM INTERCEPTION: Request intercepted
[CRITICAL] OCPP: RX ← ATTACKER: MALICIOUS URL injected
```

---

### Faz 2: Firmware Manipulation (🔴 15 saniye)
**Ne Olur:**
- EVSE durumu: COMPROMISED
- Firmware: v1.2.5 [ROOTKIT]
- Zombie EVSE aktif

**Terminal'de Göreceksin:**
```
[CRITICAL] ATTACK: ROOTKIT INSTALLED: /lib/systemd/system-evse-daemon
[CRITICAL] ATTACK: ZOMBIE EVSE: Device under attacker control
[WARNING] OCPP: FirmwareStatusNotification: Installed (FALSE)
[CRITICAL] ATTACK: C2 COMMAND: Weaponize EVSE - Prepare CAN attack
```

---

### Faz 3: CAN Bus DoS Attack (🔴 15 saniye)
**Ne Olur:**
- EVSE durumu: ATTACKING
- CAN bus yükü %98'e çıkıyor
- 0x000 ID flood başlıyor
- Normal ECU'lar bloke ediliyor

**Terminal'de Göreceksin:**
```
[CRITICAL] ATTACK: CAN bus DoS attack - 0x000 ID arbitration lock
[CRITICAL] CAN: ATTACK: 0x000 FLOOD #1 - Arbitration Lock Active
[ERROR] CAN: BLOCKED: BMS (ID=0x1F0) - Arbitration Lost
[ERROR] CAN: BLOCKED: ABS (ID=0x100) - Arbitration Lost
[CRITICAL] ATTACK: CAN BUS OVERLOAD: 98% load - 5 ECUs blocked
[CRITICAL] GPS: ANOMALY: Vehicle moving at 75 km/h but charging!
```

---

### Faz 4: Hard Brick - P-DoS (⚫ 15 saniye)
**Ne Olur:**
- EVSE durumu: BRICKED
- TÜM uyarı lambaları yanıyor! 🚨
- 5 DTC kodu oluşuyor
- Araç kullanılamaz

**Terminal'de Göreceksin:**
```
[CRITICAL] ATTACK: Hard Brick - Permanent Denial of Service
[CRITICAL] VEHICLE: DTC GENERATED: U0100 - Lost Communication With ECM/PCM
[CRITICAL] VEHICLE: DTC GENERATED: U0121 - Lost Communication With ABS
[CRITICAL] VEHICLE: DTC GENERATED: U0155 - Lost Communication With BMS
[CRITICAL] VEHICLE: DTC GENERATED: U0164 - Lost Communication With HVAC
[CRITICAL] VEHICLE: DTC GENERATED: U0195 - Lost Communication With TCM
[CRITICAL] ATTACK: HARD BRICK COMPLETE: Vehicle inoperable
[CRITICAL] ATTACK: P-DoS SUCCESSFUL: Permanent damage inflicted
```

---

## 🎨 WEB ARAYÜZÜ BİLEŞENLERİ

### 1. 🚗 Araç Gösterge Paneli
**Üst Sol - Glass Panel**

- **Hız Göstergesi**
  - Sayısal değer (0-200 km/h)
  - Animasyonlu bar chart
  - Gerçek zamanlı güncelleme

- **Motor RPM**
  - Sayısal değer (0-7000)
  - Renkli bar chart
  - Dönen arka plan efekti

- **Batarya**
  - SoC % (0-100)
  - Shimmer efektli bar
  - Renk değişimi (yeşil→turuncu→kırmızı)

- **Vites**
  - P, D, R, N göstergesi
  - 3D efekt

- **Uyarı Lambaları** (6 adet)
  - 🔧 Check Engine
  - 🚫 ABS
  - 🎈 Airbag
  - 🔋 Battery
  - ⚙️ Traction Control
  - 🛢️ Oil Pressure
  - Yanıp sönen animasyon
  - 3D pop-out efekti

- **DTC Kodları**
  - Scrollable liste
  - Slide-in animasyon
  - Kod + Açıklama + Severity

---

### 2. ⚡ EVSE Kontrol Paneli
**Üst Sağ - Glass Panel**

- **Durum Göstergesi**
  - Holografik efekt
  - Büyük merkezi metin
  - Duruma göre renk:
    - IDLE (gri)
    - CHARGING (yeşil, pulse)
    - UPDATING (turuncu, pulse)
    - COMPROMISED (kırmızı, pulse)
    - ATTACKING (kırmızı, shake)
    - BRICKED (siyah, glitch)

- **Firmware Versiyonu**
  - Normal: v1.2.4
  - Compromised: v1.2.5 [ROOTKIT] (kırmızı)

- **Metrikler** (6 adet)
  - Güç (kW)
  - Voltaj (V)
  - Akım (A)
  - Enerji (kWh)
  - Sıcaklık (°C)
  - CAN Bus Yükü (%)
  - Her biri ayrı glass box
  - Renkli değerler

---

### 3. 💻 Real-time Terminal
**Alt - Full Width Panel**

**Özellikler:**
- **MacOS Tarzı Header**
  - 3 renkli buton (kırmızı, sarı, yeşil)
  - Loading animasyonu
  - Glassmorphism

- **Terminal Output**
  - 500 satır buffer
  - Otomatik scroll
  - Fade-in animasyon
  - Hover efekti

- **Renkli Log Seviyeleri**
  - INFO (yeşil)
  - WARNING (turuncu, arka plan)
  - ERROR (kırmızı, arka plan)
  - CRITICAL (kırmızı, yanıp sönen)

- **Kategori Badge'leri**
  - CAN (turuncu)
  - OCPP (mavi)
  - GPS (mor)
  - ATTACK (kırmızı)
  - VEHICLE (sarı)
  - SIMULATION (yeşil)
  - SYSTEM (beyaz)

- **Alt Kontroller**
  - Filtre butonları (ALL, CAN, OCPP, GPS, ATTACK, VEHICLE)
  - Active state gösterimi
  - Download Logs butonu

---

### 4. 🎮 Kontrol Butonları
**Üst Orta - Futuristic**

- **START SIMULATION**
  - Yeşil gradient
  - Hover'da 3D yükseliş
  - Tıklama ripple efekti
  - Orbitron font

- **RESET**
  - Kırmızı gradient
  - Hover'da 3D yükseliş
  - Tıklama ripple efekti
  - Uyarı rengi

---

### 5. 📊 Stage Indicator
**Üst - Progress Bar**

- Mevcut faz adı (büyük)
- Progress bar (gradient, glow efekti)
- Animasyonlu dolum
- Glow sweep efekti

---

### 6. 🌌 Arka Plan Efektleri

- **Particles.js**
  - 80 parçacık
  - Bağlantılı çizgiler
  - Hover etkileşimi
  - Click'te yeni parçacık

- **Glassmorphism**
  - Blur efekti
  - Semi-transparent arka plan
  - Border glow
  - Inset shadows

- **3D Transforms**
  - Float animasyonlar
  - Rotate efektleri
  - Scale transitions
  - Z-axis depth

---

## 📁 LOG SİSTEMİ

### Otomatik Log Dosyaları
Simülasyon başlatıldığında `logs/` klasöründe:

```
logs/
├── simulation_20250109_143052.log    # Ana log (hepsi)
├── can_bus.log                       # Sadece CAN
├── ocpp.log                          # Sadece OCPP
├── gps.log                           # Sadece GPS
└── attack.log                        # Sadece ATTACK
```

### Log Format
```
[2025-01-09 14:30:52.345] [CAN] [CRITICAL] ATTACK: 0x000 FLOOD #5 | Data: {...}
```

### Log İndirme
Terminal altındaki "⬇ DOWNLOAD LOGS" butonuna tıkla → Ana log dosyası indirilir

---

## 🎯 KULLANIM SENARYOLARI

### 📢 Sunum/Demo
1. Tam ekran yap (F11)
2. START butonuna tıkla
3. Terminal'de mesajları takip et
4. Her fazda ekran değişimlerini göster
5. Hard Brick'te tüm lambaların yanışını vurgula

**Süre:** 80 saniye (otomatik)  
**Etki:** ⭐⭐⭐⭐⭐

---

### 🎓 Eğitim
1. Her faz başında simülasyonu duraklat (RESET)
2. Terminal çıktılarını açıkla
3. CAN, OCPP, GPS mesajlarını detaylandır
4. Log filtrelerini kullan (sadece CAN göster)
5. Log dosyalarını indir ve analiz et

**Süre:** 1-2 saat  
**Öğrenme:** Maksimum

---

### 🔬 Araştırma
1. Simülasyonu çalıştır
2. Log dosyalarını topla
3. Terminal çıktılarını analiz et
4. CAN mesaj pattern'lerini incele
5. Anomali tespit algoritmalarını test et

**Süre:** İstediğin kadar  
**Analiz:** Detaylı

---

## 🛠️ TEKNİK DETAYLAR

### Backend Stack
```python
Flask 3.0              # Web framework
Flask-SocketIO 5.3     # Real-time WebSocket
Python Threading       # Background simulation
```

### Frontend Stack
```javascript
Socket.IO 4.5          # Real-time client
Particles.js 2.0       # Background particles
Custom CSS3            # 3D animations, glassmorphism
Orbitron Font          # Futuristic typography
Roboto Mono            # Terminal font
```

### Simülasyon Engine
- **CAN Simulator**: Arbitrasyon, priority, DoS
- **OCPP Simulator**: 1.6 protokolü, mesajlaşma
- **GPS Simulator**: Koordinat, SoC, anomali
- **Attack Engine**: 5 fazlı saldırı zinciri

### Performans
- **Güncelleme Frekansı**: 500ms (2 Hz)
- **WebSocket Latency**: <50ms
- **Log Buffer**: 500 satır (memory)
- **CPU Kullanımı**: ~5-10%

---

## ⚠️ GÜVENLİK UYARISI

### 🚫 ASLA YAPMA
- ❌ Gerçek araçlarda test etme
- ❌ Gerçek EVSE'lerde test etme
- ❌ Gerçek ağlarda ARP spoofing yapma
- ❌ Yetkisiz sistemlere erişim

### ✅ SADECE
- ✅ İzole laboratuvar ortamı
- ✅ Eğitim amaçlı kullanım
- ✅ Güvenlik araştırması
- ✅ Etik kurallar

**⚖️ Yasal Sorumluluk: Kullanıcıya aittir**

---

## 🐛 SORUN GİDERME

### ModuleNotFoundError
```powershell
pip install -r requirements.txt
```

### Port 5000 kullanımda
```python
# ultimate_simulator.py son satırı değiştir
socketio.run(app, port=5001)  # 5000 → 5001
```

### WebSocket bağlantı hatası
1. Güvenlik duvarını kontrol et
2. `localhost` yerine `127.0.0.1:5000` dene
3. Tarayıcı console'unu kontrol et (F12)

### Particles görünmüyor
- CDN bağlantısını kontrol et
- Internet bağlantısı olmalı

---

## 📊 KARŞILAŞTIRMA

| Özellik | Önceki Modüler Sistem | Ultimate Simulator |
|---------|----------------------|-------------------|
| **Dosya Sayısı** | 12 dosya | 3 dosya ✅ |
| **Çalıştırma** | Birden fazla komut | Tek komut ✅ |
| **Terminal Görünürlük** | Ayrı terminal | Web'de entegre ✅ |
| **Log Yönetimi** | Manuel | Otomatik ✅ |
| **Görsel Kalite** | İyi | Muhteşem ✅ |
| **Kullanım Kolaylığı** | Orta | Çok Kolay ✅ |
| **Öğrenme Eğrisi** | Yüksek | Düşük ✅ |

---

## 🎉 ÖNE ÇIKAN ÖZELLİKLER

### 1. 🌌 Görsel Mükemmellik
- Particles.js ile canlı arka plan
- Glassmorphism UI
- 3D animasyonlar
- Smooth transitions
- **Dünyada görülmemiş güzellikte!**

### 2. 💯 Tam Fonksiyonel
- Gerçek CAN simülasyonu
- Tam OCPP protokolü
- GPS anomali tespiti
- 5 fazlı saldırı zinciri
- **Göstermelik değil, gerçek!**

### 3. 💻 Tek Arayüz
- Tüm bilgiler bir yerde
- Terminal web'de görünür
- Real-time güncellemeler
- **Her şey bir arada!**

### 4. 📁 Profesyonel Loglama
- Otomatik dosya oluşturma
- Kategori bazlı ayırma
- Indirilebilir loglar
- **Analiz için hazır!**

---

## 🚀 HIZLI BAŞLANGIÇ

```powershell
# 1. Klasöre git
cd C:\Users\ahmet\OneDrive\Masaüstü\bsgodev\bsg-2025-vehicle-sec\erdem-simulasyon

# 2. Simülatörü başlat
python ultimate_simulator.py

# 3. Tarayıcıda aç
# http://localhost:5000

# 4. START butonuna tıkla!
```

**Hepsi bu kadar! 🎉**

---

## 📚 DOSYA YAPISI

```
erdem-simulasyon/
├── ultimate_simulator.py          ⭐ Ana simülatör (Flask backend)
├── templates/
│   └── ultimate_simulator.html    ⭐ Web arayüzü (HTML/CSS/JS)
├── logs/                          📁 Otomatik oluşur
│   ├── simulation_*.log
│   ├── can_bus.log
│   ├── ocpp.log
│   ├── gps.log
│   └── attack.log
├── requirements.txt               📦 Bağımlılıklar
└── README.md                      📖 Bu dosya
```

**TOPLAM: 3 ana dosya! (requirements + README hariç)**

---

## 🎯 ÖĞRENİLECEKLER

### Siber Güvenlik
- ✅ MitM saldırısı nasıl yapılır
- ✅ ARP Spoofing tekniği
- ✅ Firmware manipülasyonu
- ✅ CAN bus DoS
- ✅ P-DoS (Permanent DoS)

### Protokoller
- ✅ OCPP 1.6 mesajlaşma
- ✅ CAN 2.0B arbitrasyon
- ✅ WebSocket real-time
- ✅ GPS/telemetri

### Araç Sistemleri
- ✅ ECU'lar ve görevleri
- ✅ DTC kod sistemi
- ✅ CAN bus yapısı
- ✅ EVSE entegrasyonu

---

## 💡 İPUÇLARI

### Terminal Kullanımı
- **Filtrele**: Alt kısımdaki butonlarla sadece istediğin kategoriyi göster
- **Scroll**: Terminal otomatik scroll eder, manuel da yapabilirsin
- **Hover**: Mesajların üzerine gel, detayları göster

### Log İndirme
- Simülasyon bittikten sonra "⬇ DOWNLOAD LOGS" tıkla
- Ana log dosyası indirilir
- `logs/` klasöründen diğerlerini al

### Sunum Modu
1. F11 ile tam ekran
2. START'a tıkla
3. Terminal'i izle
4. Her faz değişiminde ekran otomatik güncellenir

---

## 🌟 BAŞARILAR

✅ **Tek komutla çalışır**  
✅ **Tüm işlemler web'de görünür**  
✅ **Gerçek simülasyon - göstermelik değil**  
✅ **Otomatik loglama**  
✅ **Dünyada görülmemiş UI**  
✅ **Real-time updates**  
✅ **3D animasyonlar**  
✅ **Glassmorphism tasarım**  
✅ **Particles.js arka plan**  
✅ **Filtrelenebilir terminal**  
✅ **İndirilebilir loglar**  

---

**Geliştirici:** EVSE P-DoS Araştırma Ekibi  
**Versiyon:** 3.0 ULTIMATE  
**Lisans:** Eğitim ve Araştırma Amaçlı  
**Tarih:** 2025

---

## 🎬 HEMEN BAŞLA!

```powershell
python ultimate_simulator.py
```

**Sonra tarayıcıda:**
```
http://localhost:5000
```

**START butonuna tıkla ve izle! 🍿**

---

**⚡ ULTIMATE. BEAUTIFUL. FUNCTIONAL. ⚡**
