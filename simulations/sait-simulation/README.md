# V2G Protocol Manipulation Simülasyonu

## Senaryo Açıklaması

Bu simülasyon, **V2G (Vehicle-to-Grid) Protokol Manipülasyonu** saldırısını ve bu saldırının **mikro şebeke dengesizliğine** (Microgrid Destabilization) nasıl yol açabileceğini göstermektedir.

### Saldırı Vektörü

1. **ISO 15118 / OCPP Protokolü Manipülasyonu**: Saldırgan, EV ve şarj istasyonu arasındaki iletişimi ele geçirerek sahte V2G komutları enjekte eder.
2. **Sahte Enerji Transfer Verileri**: Aracın şebekeye gönderdiği enerji miktarı manipüle edilir.
3. **Koordineli Saldırı**: Birden fazla EV aynı anda manipüle edilerek şebekede ani voltaj/frekans dalgalanmaları oluşturulur.

### Simülasyon Bileşenleri

| Dosya | Açıklama |
|-------|----------|
| `csms_server.py` | OCPP 1.6 CSMS (Central System Management Server) |
| `charging_station.py` | Şarj İstasyonu (EVSE) Simülatörü |
| `ev_simulator.py` | Elektrikli Araç (EV) ve V2G Simülatörü |
| `microgrid_monitor.py` | Mikro Şebeke İzleme ve Anomali Tespit Sistemi |
| `v2g_attacker.py` | V2G Protokol Manipülasyon Saldırısı Simülatörü |

### Çalıştırma

```bash
# 1. Sanal ortam oluştur
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. CSMS sunucusunu başlat (Terminal 1)
python csms_server.py

# 4. Şarj istasyonunu başlat (Terminal 2)
python charging_station.py

# 5. Normal EV simülasyonu (Terminal 3)
python ev_simulator.py --mode normal

# 6. Mikro şebeke izleyicisini başlat (Terminal 4)
python microgrid_monitor.py

# 7. Saldırı simülasyonu (Terminal 5)
python v2g_attacker.py --attack-type injection
```

### Saldırı Modları

- `normal`: Normal V2G operasyonu (şarj/deşarj)
- `injection`: Sahte enerji verisi enjeksiyonu
- `flooding`: Aşırı V2G komutu göndererek DoS
- `destabilize`: Koordineli saldırı ile şebeke dengesizliği

### Anomali Tespit Mantığı

1. **Enerji Akışı Tutarsızlığı**: Talep edilen vs. gerçek enerji transferi
2. **Frekans Sapması**: Normalde 50Hz, tolerans ±0.5Hz
3. **Voltaj Dalgalanması**: Normalde 230V, tolerans ±10V
4. **Ani Yük Değişimi**: Beklenmeyen güç talebi artışı

## Lisans

BSG 2025 Vehicle Security Projesi
