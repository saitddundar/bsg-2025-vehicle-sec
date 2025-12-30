#!/usr/bin/env python3
"""
CSMS (Central System Management Server) - OCPP 1.6
Central Server for V2G Protocol Manipulation Simulation

This server:
1. Accepts connections from charging stations
2. Coordinates V2G (Vehicle-to-Grid) energy transfer commands
3. Monitors microgrid status
"""

import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
import json
import websockets
from ocpp.v16 import call_result, call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus
from ocpp.routing import on

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MicrogridState:
    """Microgrid state"""
    def __init__(self):
        self.frequency = 50.0  # Hz (Nominal)
        self.voltage = 230.0   # V (Nominal)
        self.total_load = 0.0  # kW
        self.v2g_power = 0.0   # kW (negative: vehicle to grid)
        self.connected_evs = {}
        self.alerts = []
    
    def to_dict(self):
        return {
            'frequency': self.frequency,
            'voltage': self.voltage,
            'total_load': self.total_load,
            'v2g_power': self.v2g_power,
            'connected_evs': len(self.connected_evs),
            'status': 'ANOMALY' if self.alerts else 'NORMAL'
        }


# Global microgrid state
microgrid = MicrogridState()


class ChargePointHandler(cp):
    """OCPP 1.6 Charge Point Handler"""
    
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.energy_imported = 0  # Wh
        self.energy_exported = 0  # Wh (V2G)
        self.current_power = 0    # W
        self.v2g_enabled = False
    
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        """When charging station boots"""
        logger.info(f"[CONNECT] STATION CONNECTED: {self.id}")
        logger.info(f"   Vendor: {charge_point_vendor}")
        logger.info(f"   Model: {charge_point_model}")
        
        microgrid.connected_evs[self.id] = {
            'vendor': charge_point_vendor,
            'model': charge_point_model,
            'connected_at': datetime.now(timezone.utc).isoformat(),
            'status': 'Available'
        }
        
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=10,
            status=RegistrationStatus.accepted
        )
    
    @on('Heartbeat')
    async def on_heartbeat(self):
        """Heartbeat - Station is still active"""
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat()
        )
    
    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        """Station status notification"""
        logger.info(f"[STATUS] STATUS CHANGE: {self.id}")
        logger.info(f"   Connector: {connector_id}")
        logger.info(f"   Status: {status}")
        
        if self.id in microgrid.connected_evs:
            microgrid.connected_evs[self.id]['status'] = status
        
        return call_result.StatusNotification()
    
    @on('MeterValues')
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        """Meter values - Energy flow"""
        for val in meter_value:
            for sample in val.get('sampled_value', []):
                measurand = sample.get('measurand', 'Energy.Active.Import.Register')
                value = float(sample.get('value', 0))
                unit = sample.get('unit', 'Wh')
                
                # Detect V2G
                if 'Export' in measurand:
                    self.energy_exported = value
                    power_direction = "-> GRID (V2G)"
                    microgrid.v2g_power = value / 1000  # kW
                else:
                    self.energy_imported = value
                    power_direction = "<- VEHICLE"
                
                logger.info(f"[ENERGY] ENERGY FLOW: {self.id}")
                logger.info(f"   Measurand: {measurand}")
                logger.info(f"   Value: {value} {unit}")
                logger.info(f"   Direction: {power_direction}")
                
                # Anomaly check
                self._check_v2g_anomaly(measurand, value)
        
        return call_result.MeterValues()
    
    @on('DataTransfer')
    async def on_data_transfer(self, vendor_id, message_id=None, data=None):
        """Custom data transfer - For V2G commands"""
        logger.info(f"[DATA] DATA TRANSFER: {self.id}")
        logger.info(f"   Vendor: {vendor_id}")
        logger.info(f"   Message ID: {message_id}")
        
        try:
            if data:
                payload = json.loads(data) if isinstance(data, str) else data
                logger.info(f"   Data: {json.dumps(payload, indent=2)}")
                
                # Process V2G commands
                if message_id == 'V2G_SetDischargeSchedule':
                    return await self._handle_v2g_schedule(payload)
                elif message_id == 'V2G_StartDischarge':
                    return await self._handle_v2g_start(payload)
        except json.JSONDecodeError:
            logger.warning(f"   Raw Data: {data}")
        
        return call_result.DataTransfer(status='Accepted')
    
    async def _handle_v2g_schedule(self, payload):
        """Process V2G discharge schedule"""
        schedule = payload.get('schedule', [])
        logger.info(f"[V2G] V2G SCHEDULE RECEIVED: {self.id}")
        
        for slot in schedule:
            start = slot.get('start_time')
            end = slot.get('end_time')
            power = slot.get('power_kw', 0)
            logger.info(f"   {start} - {end}: {power} kW")
        
        self.v2g_enabled = True
        return call_result.DataTransfer(status='Accepted', data=json.dumps({
            'v2g_status': 'scheduled',
            'slots': len(schedule)
        }))
    
    async def _handle_v2g_start(self, payload):
        """Start V2G discharge"""
        power_kw = payload.get('power_kw', 0)
        duration_min = payload.get('duration_minutes', 60)
        
        logger.info(f"[V2G] V2G DISCHARGE STARTED: {self.id}")
        logger.info(f"   Power: {power_kw} kW")
        logger.info(f"   Duration: {duration_min} minutes")
        
        # Update microgrid
        microgrid.v2g_power += power_kw
        microgrid.total_load -= power_kw  # V2G reduces load
        
        return call_result.DataTransfer(status='Accepted', data=json.dumps({
            'v2g_status': 'discharging',
            'power_kw': power_kw
        }))
    
    def _check_v2g_anomaly(self, measurand, value):
        """V2G anomaly check"""
        # Sudden high energy transfer
        if 'Export' in measurand and value > 50000:  # Over 50 kWh
            alert = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'station_id': self.id,
                'type': 'HIGH_V2G_EXPORT',
                'value': value,
                'message': f'Abnormally high V2G energy transfer: {value} Wh'
            }
            microgrid.alerts.append(alert)
            logger.warning(f"[ALERT] ANOMALY: {alert['message']}")


async def on_connect(websocket):
    """New connection handler"""
    try:
        # Get path for websockets v11+
        charge_point_id = websocket.request.path.strip('/')
        
        if not charge_point_id:
            charge_point_id = f"CP_{datetime.now().strftime('%H%M%S')}"
            logger.warning(f"[WARN] Path empty, using default ID: {charge_point_id}")
        
        logger.info(f"[CONNECT] Connection request: {charge_point_id}")
        
        cp_handler = ChargePointHandler(charge_point_id, websocket)
        
        await cp_handler.start()
        
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"[INFO] {charge_point_id} closed connection")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(f"[ERROR] {charge_point_id} connection error: {e}")
    except Exception as e:
        logger.error(f"[ERROR] Connection error: {e}", exc_info=True)
    finally:
        # Clean up connected EVs
        if charge_point_id in microgrid.connected_evs:
            del microgrid.connected_evs[charge_point_id]


async def microgrid_status_task():
    """Periodic microgrid status print"""
    while True:
        await asyncio.sleep(15)
        
        status = microgrid.to_dict()
        logger.info(f"\n{'='*60}")
        logger.info(f"[GRID] MICROGRID STATUS")
        logger.info(f"{'='*60}")
        logger.info(f"   Frequency: {status['frequency']:.2f} Hz")
        logger.info(f"   Voltage: {status['voltage']:.1f} V")
        logger.info(f"   Total Load: {status['total_load']:.2f} kW")
        logger.info(f"   V2G Power: {status['v2g_power']:.2f} kW")
        logger.info(f"   Connected EVs: {status['connected_evs']}")
        logger.info(f"   Status: {status['status']}")
        
        if microgrid.alerts:
            logger.warning(f"   [!] Active Alerts: {len(microgrid.alerts)}")
        logger.info(f"{'='*60}\n")


async def main():
    """Main server startup"""
    logger.info("="*60)
    logger.info("[START] V2G CSMS SERVER STARTING")
    logger.info("="*60)
    logger.info("Protocol: OCPP 1.6")
    logger.info("Port: 9000")
    logger.info("V2G Support: Active")
    logger.info("="*60)
    
    # WebSocket server
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )
    
    logger.info("[OK] Server started successfully!")
    logger.info("[INFO] Connect to: ws://localhost:9000/STATION_ID")
    logger.info("")
    
    # Microgrid monitoring task
    status_task = asyncio.create_task(microgrid_status_task())
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("\n[STOP] Server shutting down...")
        status_task.cancel()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped")
