import time
import json
import os


def ids_baslat():
    print("🧠 IDS Aktif. Analiz edilen: csms_log.txt | Alarmlar: alerts_log.txt\n")

    okunacak_log = "csms_log.txt"
    alert_log = "alerts_log.txt"
    beklenen_alanlar = {"status", "timestamp", "vendor"}

    # Log dosyası yoksa bekle
    while not os.path.exists(okunacak_log):
        time.sleep(1)

    with open(okunacak_log, "r") as f:
        f.seek(0, 2)  # Dosyanın sonuna git

        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            try:
                # Log formatı: [ZAMAN] {JSON} -> JSON kısmını ayıkla
                json_str = line.split("] ", 1)[1]
                mesaj = json.loads(json_str)
                timestamp = line.split("] ")[0][1:]

                mevcut_alanlar = set(mesaj.keys())

                # SALDIRI TESPİTİ
                if mevcut_alanlar != beklenen_alanlar:
                    fazla_alan = mevcut_alanlar - beklenen_alanlar
                    uyari = f"🚨 [{timestamp}] SALDIRI TESPİT EDİLDİ! Eklenen Alan: {fazla_alan} | Boyut: {len(line)} byte"
                    print(uyari)

                    # ALARMLARI AYRI DOSYAYA YAZ
                    with open(alert_log, "a", encoding="utf-8") as f_alert:
                        f_alert.write(uyari + "\n")
                else:
                    print(f"✅ [{timestamp}] Güvenli trafik.")

            except Exception as e:
                pass


if __name__ == "__main__":
    ids_baslat()