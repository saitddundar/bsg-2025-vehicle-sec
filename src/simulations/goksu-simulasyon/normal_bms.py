import can
import time

def send_bms_heartbeat():
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    
    # ID 0x100: BMS
    # Data [0x01]: "Enerji AL / Şarj Et" komutu
    msg = can.Message(arbitration_id=0x100, data=[0x01], is_extended_id=False)
    
    print("BMS Başlatıldı: Şarj isteği gönderiliyor (ID: 0x100)...")
    
    try:
        while True:
            bus.send(msg)
            # Her 0.5 saniyede bir "Ben buradayım, şarj et" diyor
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nBMS kapatıldı.")

if __name__ == "__main__":
    send_bms_heartbeat()