# Phantom SoC (Kapasite Sahtekârlığı) Simülasyonu

Bu projede elektrikli araç şarj altyapısında görülebilecek
Phantom SoC (State of Charge Manipulation) saldırısı
uygulamalı olarak simüle edilmiştir.

## Senaryo
- EV gerçek SoC değerini gönderir
- MITM saldırganı bu değeri ağ üzerinde değiştirir
- CSMS tutarsızlığı tespit ederek şarj oturumunu durdurur

## Bileşenler
- ev.py : Elektrikli araç simülasyonu
- mitm.py : MITM saldırı simülasyonu
- csms.py : Merkezi şarj yönetim sistemi

## Çalıştırma
```bash
python csms.py
python mitm.py
python ev.py
