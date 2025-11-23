import can

def evcc_monitor():
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    
    print("EVCC (Şarj Beyni) Dinlemede...")
    print("Beklenen durum: Sadece BMS (0x100) sinyali.")

    # Durum kontrolü için flag'ler
    charging_requested = False
    discharging_requested = False
    
    # Son mesaj zamanlarını tutmak için (Timeout kontrolü simülasyonu)
    import time
    last_bms_time = 0
    last_ghost_time = 0

    try:
        while True:
            msg = bus.recv(timeout=1.0) # Mesaj bekle
            current_time = time.time()

            if msg:
                if msg.arbitration_id == 0x100 and msg.data[0] == 0x01:
                    last_bms_time = current_time
                    charging_requested = True
                    # BMS'den normal mesaj geldi
                
                elif msg.arbitration_id == 0x666 and msg.data[0] == 0x02:
                    last_ghost_time = current_time
                    discharging_requested = True
                    print(f"UYARI: Bilinmeyen modülden (0x666) Deşarj isteği alındı! [cite: 21]")

            # Durumları Değerlendir (Sinyal zaman aşımına uğramadıysa aktiftir)
            bms_active = (current_time - last_bms_time) < 2.0
            ghost_active = (current_time - last_ghost_time) < 2.0

            # MANTIK KARAR MEKANİZMASI
            if bms_active and not ghost_active:
                print("[DURUM NORMAL]: Şarj Başlatılıyor... (Enerji AL)")
            
            elif bms_active and ghost_active:
                # Dokümandaki "Mantık Çöküşü" 
                print("\n!!! KRİTİK HATA (LOGIC CRASH) !!!")
                print("ÇELİŞKİ TESPİT EDİLDİ: Hem 'Enerji AL' hem 'Enerji VER' komutu var.")
                print("SİSTEM KİLİTLENDİ: Şarj reddediliyor. Hizmet Engellendi (DoS). [cite: 18, 19]")
                print("-" * 50)
            
            elif not bms_active and not ghost_active:
                print("Sistem beklemede...", end='\r')

    except KeyboardInterrupt:
        print("\nEVCC Kapatıldı.")

if __name__ == "__main__":
    evcc_monitor()