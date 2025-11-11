# istasyon.py
import asyncio, json, random, argparse, time
import websockets

def now_ms(): 
    import time
    return int(time.time() * 1000)

async def run(args):
    uri = args.uri
    sid = args.station_id
    card = args.card
    rnd = random.Random(42)

    async with websockets.connect(uri, subprotocols=['ocpp1.6']) as ws:
        # HELLO
        await ws.send(json.dumps({"type":"hello","station_id":sid}))
        start_t = time.time()

        async def heartbeat_task():
            while True:
                await ws.send(json.dumps({"type":"heartbeat","station_id":sid}))
                await asyncio.sleep(5)

        async def status_task():
            status = "Available"
            power = 0.0
            while True:
                if args.state_mismatch:
                    status = "Available"; power = 3.5
                else:
                    status = "Charging" if card else "Available"
                    power = 7.2 if status=="Charging" else 0.0
                await ws.send(json.dumps({"type":"status","station_id":sid,"status":status,"power_kw":power}))
                await asyncio.sleep(3)

        async def gps_task():
            base = (39.9208, 32.8541) if "001" in sid else (41.0151, 28.9795)
            while True:
                lat, lon = base
                if args.gps_spoof:
                    lat += 0.02; lon += 0.02
                await ws.send(json.dumps({"type":"gps","station_id":sid,"lat":lat,"lon":lon}))
                await asyncio.sleep(4)

        async def charge_session():
            nonlocal card
            if args.rfid_clone:
                card = "CLONED-XXXX"
            await ws.send(json.dumps({"type":"start_tx","station_id":sid,"card_id":card}))
            energy = 0.0
            while time.time()-start_t < args.duration:
                if args.meter_spoof and random.random()<0.2:
                    energy += random.choice([3.5, -0.2])
                else:
                    energy += 0.05
                power = 7.0
                await ws.send(json.dumps({"type":"meter","station_id":sid,"energy_kwh":round(energy,3),"power_kw":power}))
                if args.dos_burst:
                    for _ in range(40):
                        await ws.send(json.dumps({"type":"meter","station_id":sid,"energy_kwh":round(energy,3),"power_kw":power}))
                await asyncio.sleep(1.5)
            await ws.send(json.dumps({"type":"stop_tx","station_id":sid}))

        tasks = [
            asyncio.create_task(heartbeat_task()),
            asyncio.create_task(status_task()),
            asyncio.create_task(gps_task()),
            asyncio.create_task(charge_session()),
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default="ws://127.0.0.1:8765")
    ap.add_argument("--station-id", default="EVSE-TR-001")
    ap.add_argument("--card", default="55AA11FF99")
    ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--rfid-clone", action="store_true")
    ap.add_argument("--meter-spoof", action="store_true")
    ap.add_argument("--gps-spoof", action="store_true")
    ap.add_argument("--dos-burst", action="store_true")
    ap.add_argument("--state-mismatch", action="store_true")
    args = ap.parse_args()
    asyncio.run(run(args))
