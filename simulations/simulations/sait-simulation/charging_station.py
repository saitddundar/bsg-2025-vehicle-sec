#!/usr/bin/env python3
"""
Charging Station (EVSE) Simulator
V2G Protocol Manipulation Simulation

This simulator:
1. Connects to CSMS and registers itself
2. Simulates EV connection
3. Supports V2G (Vehicle-to-Grid) energy transfer
4. Reports charge/discharge status
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from enum import Enum
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class V2GMode(Enum):
    """V2G Operating Modes"""
    IDLE = "idle"
    CHARGING = "charging"      # Grid to Vehicle
    DISCHARGING = "discharging"  # Vehicle to Grid (V2G)


class ChargingStation(cp):
    """OCPP 1.6 Charging Station"""
    
    def __init__(self, station_id, websocket):
        super().__init__(station_id, websocket)
        self.station_id = station_id
        self.v2g_mode = V2GMode.IDLE
        self.energy_imported = 0.0  # Wh
        self.energy_exported = 0.0  # Wh
        self.current_power = 0.0    # W
        self.ev_connected = False
        self.ev_soc = 80  # Battery state (%)
        self.max_charge_power = 22000  # W (22 kW)
        self.max_discharge_power = 11000  # W (11 kW)
    
    async def send_boot_notification(self):
        """Register with CSMS"""
        request = call.BootNotification(
            charge_point_model="V2G-Station-Pro",
            charge_point_vendor="BSG-Energy"
        )
        
        logger.info("[BOOT] Sending BootNotification to CSMS...")
        
        try:
            response = await self.call(request)
            
            if response.status == RegistrationStatus.accepted:
                logger.info(f"[OK] Accepted by CSMS!")
                logger.info(f"   Heartbeat interval: {response.interval}s")
                return response.interval
            else:
                logger.error(f"[ERROR] Rejected by CSMS: {response.status}")
                return None
        except Exception as e:
            logger.error(f"[ERROR] BootNotification error: {e}")
            return None
    
    async def send_heartbeat_loop(self, interval):
        """Send regular heartbeat"""
        while True:
            await asyncio.sleep(interval)
            
            request = call.Heartbeat()
            
            try:
                response = await self.call(request)
                logger.debug(f"[HEARTBEAT] Server time: {response.current_time}")
            except Exception as e:
                logger.error(f"[ERROR] Heartbeat error: {e}")
    
    async def send_status_notification(self, status):
        """Send status notification"""
        request = call.StatusNotification(
            connector_id=1,
            error_code='NoError',
            status=status
        )
        
        try:
            await self.call(request)
            logger.info(f"[STATUS] Status updated: {status}")
        except Exception as e:
            logger.error(f"[ERROR] StatusNotification error: {e}")
    
    async def send_meter_values(self):
        """Send energy meter values"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        sampled_values = []
        
        # Import (Grid to Vehicle)
        if self.v2g_mode == V2GMode.CHARGING:
            sampled_values.append({
                'value': str(int(self.energy_imported)),
                'context': 'Sample.Periodic',
                'format': 'Raw',
                'measurand': 'Energy.Active.Import.Register',
                'unit': 'Wh'
            })
        
        # Export (Vehicle to Grid - V2G)
        if self.v2g_mode == V2GMode.DISCHARGING:
            sampled_values.append({
                'value': str(int(self.energy_exported)),
                'context': 'Sample.Periodic',
                'format': 'Raw',
                'measurand': 'Energy.Active.Export.Register',
                'unit': 'Wh'
            })
        
        # Instantaneous power
        sampled_values.append({
            'value': str(int(abs(self.current_power))),
            'context': 'Sample.Periodic',
            'format': 'Raw',
            'measurand': 'Power.Active.Import' if self.v2g_mode == V2GMode.CHARGING else 'Power.Active.Export',
            'unit': 'W'
        })
        
        meter_value = [{
            'timestamp': timestamp,
            'sampled_value': sampled_values
        }]
        
        request = call.MeterValues(
            connector_id=1,
            meter_value=meter_value
        )
        
        try:
            await self.call(request)
        except Exception as e:
            logger.error(f"[ERROR] MeterValues error: {e}")
    
    async def send_v2g_data(self, data):
        """Send V2G custom data"""
        request = call.DataTransfer(
            vendor_id='BSG-Energy',
            message_id='V2G_Status',
            data=json.dumps(data)
        )
        
        try:
            response = await self.call(request)
            if response.status == 'Accepted':
                logger.info(f"[V2G] V2G data sent")
        except Exception as e:
            logger.error(f"[ERROR] DataTransfer error: {e}")
    
    async def simulate_charging(self):
        """Charging simulation"""
        self.v2g_mode = V2GMode.CHARGING
        self.current_power = self.max_charge_power
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[CHARGE] CHARGING STARTED")
        logger.info(f"{'='*60}")
        logger.info(f"   Mode: Grid -> Vehicle (G2V)")
        logger.info(f"   Power: {self.current_power/1000:.1f} kW")
        logger.info(f"   Battery: {self.ev_soc}%")
        logger.info(f"{'='*60}\n")
        
        await self.send_status_notification('Charging')
        
        while self.ev_soc < 100 and self.v2g_mode == V2GMode.CHARGING:
            await asyncio.sleep(5)
            
            # Calculate energy (in 5 seconds)
            energy_wh = (self.current_power * 5) / 3600
            self.energy_imported += energy_wh
            self.ev_soc += 0.5  # 0.5% every 5 seconds
            
            logger.info(f"[CHARGE] Charging... SoC: {self.ev_soc:.1f}% | Energy: {self.energy_imported/1000:.2f} kWh")
            
            await self.send_meter_values()
    
    async def simulate_discharging(self, power_kw=11, duration_min=10):
        """V2G Discharge simulation (Vehicle-to-Grid)"""
        self.v2g_mode = V2GMode.DISCHARGING
        self.current_power = power_kw * 1000  # kW -> W
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[V2G] V2G DISCHARGE STARTED")
        logger.info(f"{'='*60}")
        logger.info(f"   Mode: Vehicle -> Grid (V2G)")
        logger.info(f"   Power: {power_kw:.1f} kW")
        logger.info(f"   Duration: {duration_min} minutes")
        logger.info(f"   Battery: {self.ev_soc}%")
        logger.info(f"{'='*60}\n")
        
        await self.send_status_notification('Charging')  # No specific V2G status in OCPP
        
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + (duration_min * 60)
        
        while asyncio.get_event_loop().time() < end_time and self.ev_soc > 20:
            await asyncio.sleep(5)
            
            # Calculate energy
            energy_wh = (self.current_power * 5) / 3600
            self.energy_exported += energy_wh
            self.ev_soc -= 0.3  # 0.3% every 5 seconds
            
            logger.info(f"[V2G] Discharging... SoC: {self.ev_soc:.1f}% | To Grid: {self.energy_exported/1000:.2f} kWh")
            
            await self.send_meter_values()
            
            # Send V2G status
            await self.send_v2g_data({
                'mode': 'V2G',
                'power_kw': power_kw,
                'soc': self.ev_soc,
                'energy_exported_kwh': self.energy_exported / 1000
            })
        
        self.v2g_mode = V2GMode.IDLE
        self.current_power = 0
        logger.info(f"\n[OK] V2G discharge complete! Total: {self.energy_exported/1000:.2f} kWh")
    
    async def start(self):
        """Start station"""
        # Boot notification
        interval = await self.send_boot_notification()
        
        if interval:
            # Status notification
            await self.send_status_notification('Available')
            
            # Simulate EV connection
            await asyncio.sleep(3)
            self.ev_connected = True
            logger.info("[CONNECT] EV connected!")
            await self.send_status_notification('Preparing')
            
            # Run heartbeat and simulation in parallel
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self._main_loop(),
                return_exceptions=True
            )
        else:
            logger.error("[ERROR] Boot failed, stopping station")
    
    async def _main_loop(self):
        """Main operation loop"""
        await asyncio.sleep(5)
        
        # First charge
        await self.simulate_charging()
        
        await asyncio.sleep(3)
        
        # Then V2G discharge
        await self.simulate_discharging(power_kw=11, duration_min=5)
        
        await self.send_status_notification('Available')
        
        # Wait
        while True:
            await asyncio.sleep(60)


async def main():
    """Main program"""
    station_id = "EVSE_001"
    csms_url = f"ws://localhost:9000/{station_id}"
    
    logger.info("="*60)
    logger.info("[START] CHARGING STATION STARTING")
    logger.info("="*60)
    logger.info(f"   Station ID: {station_id}")
    logger.info(f"   CSMS URL: {csms_url}")
    logger.info(f"   V2G Support: Active")
    logger.info(f"   Max Charge: 22 kW")
    logger.info(f"   Max Discharge (V2G): 11 kW")
    logger.info("="*60)
    
    try:
        async with websockets.connect(
            csms_url,
            subprotocols=['ocpp1.6']
        ) as ws:
            logger.info("[OK] Connected to CSMS!")
            
            station = ChargingStation(station_id, ws)
            
            await asyncio.gather(
                cp.start(station),
                station.start(),
                return_exceptions=True
            )
            
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"[ERROR] Connection error: CSMS may not be running ({e})")
    except Exception as e:
        logger.error(f"[ERROR] Station error: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Station stopped")
