# veri_toplayıcı.py
import json, csv, pathlib
from datetime import datetime

SRC = pathlib.Path("events.jsonl")
CSV = pathlib.Path("anomaly_summary.csv")

def ts_str(ms):
    return datetime.fromtimestamp(ms/1000).strftime("%Y-%m-%d %H:%M:%S")

counts = {}
rows = []
if not SRC.exists():
    print("events.jsonl bulunamadı. Önce simülasyonu çalıştır.")
else:
    with SRC.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            ev = json.loads(line)
            if ev.get("level") == "ALERT":
                code = ev.get("event")
                counts[code] = counts.get(code, 0) + 1
                rows.append([ts_str(ev["ts"]), ev.get("station_id","?"), code, ev.get("detail","")])

    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time","station_id","anomaly_code","detail"])
        w.writerows(rows)

    print("Anomali sayımları:", counts)
    print("CSV yazıldı ->", CSV.resolve())
