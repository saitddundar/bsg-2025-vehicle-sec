# gps_simulator.py
import asyncio, json, argparse, random
import websockets

async def main(a):
    uri = a.uri
    async with websockets.connect(uri) as ws:
        while True:
            lat, lon = a.lat, a.lon
            # spoof istenirse ufak sapma uygula
            if a.spoof:
                lat += random.choice([-1, 1]) * 0.02
                lon += random.choice([-1, 1]) * 0.02

            msg = {
                "type": "gps",
                "station_id": a.station_id,
                "lat": round(lat, 6),
                "lon": round(lon, 6)
            }
            await ws.send(json.dumps(msg))
            await asyncio.sleep(a.period)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--uri", default="ws://127.0.0.1:8765")
    p.add_argument("--station-id", default="EVSE-TR-001")
    p.add_argument("--lat", type=float, default=39.9208)
    p.add_argument("--lon", type=float, default=32.8541)
    p.add_argument("--period", type=float, default=3.0)
    p.add_argument("--spoof", action="store_true")
    a = p.parse_args()
    asyncio.run(main(a))
