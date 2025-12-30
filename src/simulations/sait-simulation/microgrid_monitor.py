#!/usr/bin/env python3
"""
Microgrid Monitoring and Anomaly Detection System
V2G Protocol Manipulation Simulation

This system:
1. Monitors microgrid parameters (voltage, frequency, power)
2. Tracks V2G energy flows
3. Detects abnormal conditions
4. Performs attack detection
"""

import asyncio
import logging
import random
import math
from datetime import datetime
from enum import Enum
from collections import deque

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ATTACK = "ATTACK"


class MicrogridMonitor:
    """Microgrid Monitoring System"""
    
    def __init__(self):
        # Nominal values
        self.NOMINAL_FREQUENCY = 50.0  # Hz
        self.NOMINAL_VOLTAGE = 230.0   # V
        
        # Tolerances
        self.FREQ_TOLERANCE = 0.5  # +/-0.5 Hz
        self.VOLTAGE_TOLERANCE = 23.0  # +/-23V (10%)
        
        # Current values
        self.frequency = 50.0
        self.voltage = 230.0
        self.total_load = 100.0  # kW (base load)
        self.total_generation = 120.0  # kW
        self.v2g_power = 0.0  # kW
        
        # EVs
        self.connected_evs = {}
        self.ev_v2g_power = {}  # V2G power per EV
        
        # Historical data (for anomaly detection)
        self.frequency_history = deque(maxlen=60)
        self.voltage_history = deque(maxlen=60)
        self.v2g_history = deque(maxlen=60)
        
        # Anomaly counters
        self.total_checks = 0
        self.anomaly_count = 0
        self.attack_indicators = []
        
        logger.info(f"\n{'='*70}")
        logger.info(f"[START] MICROGRID MONITORING SYSTEM STARTED")
        logger.info(f"{'='*70}")
        logger.info(f"   Nominal Frequency: {self.NOMINAL_FREQUENCY} Hz")
        logger.info(f"   Nominal Voltage: {self.NOMINAL_VOLTAGE} V")
        logger.info(f"   Frequency Tolerance: +/-{self.FREQ_TOLERANCE} Hz")
        logger.info(f"   Voltage Tolerance: +/-{self.VOLTAGE_TOLERANCE} V")
        logger.info(f"{'='*70}\n")
    
    def add_ev(self, ev_id, max_power_kw=11):
        """Add EV connection"""
        self.connected_evs[ev_id] = {
            'connected_at': datetime.now().isoformat(),
            'max_power_kw': max_power_kw,
            'current_power_kw': 0,
            'mode': 'idle'
        }
        self.ev_v2g_power[ev_id] = 0
        logger.info(f"[CONNECT] EV Connected: {ev_id} (Max: {max_power_kw} kW)")
    
    def remove_ev(self, ev_id):
        """Remove EV connection"""
        if ev_id in self.connected_evs:
            del self.connected_evs[ev_id]
            del self.ev_v2g_power[ev_id]
            logger.info(f"[DISCONNECT] EV Disconnected: {ev_id}")
    
    def update_v2g_power(self, ev_id, power_kw):
        """Update EV's V2G power"""
        if ev_id in self.connected_evs:
            self.ev_v2g_power[ev_id] = power_kw
            self.connected_evs[ev_id]['current_power_kw'] = power_kw
            self.connected_evs[ev_id]['mode'] = 'v2g' if power_kw > 0 else 'idle'
    
    def simulate_grid_dynamics(self):
        """Simulate grid dynamics"""
        # Total V2G power
        self.v2g_power = sum(self.ev_v2g_power.values())
        
        # Power balance
        power_balance = self.total_generation + self.v2g_power - self.total_load
        
        # Frequency deviation (based on power balance)
        # Positive balance -> frequency increases, negative -> decreases
        freq_deviation = power_balance * 0.01  # Simple model
        self.frequency = self.NOMINAL_FREQUENCY + freq_deviation + random.uniform(-0.1, 0.1)
        
        # Voltage deviation
        voltage_deviation = power_balance * 0.1 + random.uniform(-2, 2)
        self.voltage = self.NOMINAL_VOLTAGE + voltage_deviation
        
        # Add to history
        self.frequency_history.append(self.frequency)
        self.voltage_history.append(self.voltage)
        self.v2g_history.append(self.v2g_power)
    
    def detect_anomaly(self):
        """Detect anomaly"""
        self.total_checks += 1
        anomalies = []
        
        # 1. Frequency deviation check
        freq_deviation = abs(self.frequency - self.NOMINAL_FREQUENCY)
        if freq_deviation > self.FREQ_TOLERANCE:
            anomalies.append({
                'type': 'FREQUENCY_DEVIATION',
                'level': AlertLevel.WARNING if freq_deviation < 1.0 else AlertLevel.CRITICAL,
                'value': self.frequency,
                'deviation': freq_deviation,
                'message': f'Frequency deviation: {self.frequency:.2f} Hz (Deviation: {freq_deviation:.2f} Hz)'
            })
        
        # 2. Voltage deviation check
        voltage_deviation = abs(self.voltage - self.NOMINAL_VOLTAGE)
        if voltage_deviation > self.VOLTAGE_TOLERANCE:
            anomalies.append({
                'type': 'VOLTAGE_DEVIATION',
                'level': AlertLevel.WARNING if voltage_deviation < 30 else AlertLevel.CRITICAL,
                'value': self.voltage,
                'deviation': voltage_deviation,
                'message': f'Voltage deviation: {self.voltage:.1f} V (Deviation: {voltage_deviation:.1f} V)'
            })
        
        # 3. Rapid V2G change check
        if len(self.v2g_history) >= 5:
            recent_v2g = list(self.v2g_history)[-5:]
            v2g_change = max(recent_v2g) - min(recent_v2g)
            if v2g_change > 30:  # More than 30 kW sudden change
                anomalies.append({
                    'type': 'RAPID_V2G_CHANGE',
                    'level': AlertLevel.WARNING,
                    'value': v2g_change,
                    'message': f'Rapid V2G power change: {v2g_change:.1f} kW'
                })
        
        # 4. Coordinated attack detection
        active_v2g_count = sum(1 for p in self.ev_v2g_power.values() if p > 0)
        if active_v2g_count >= 3 and self.v2g_power > 50:
            anomalies.append({
                'type': 'COORDINATED_V2G',
                'level': AlertLevel.ATTACK,
                'value': active_v2g_count,
                'message': f'Coordinated V2G detected: {active_v2g_count} EVs discharging simultaneously ({self.v2g_power:.1f} kW)'
            })
        
        # 5. Excessive V2G power
        if self.v2g_power > 100:  # Over 100 kW
            anomalies.append({
                'type': 'EXCESSIVE_V2G',
                'level': AlertLevel.CRITICAL,
                'value': self.v2g_power,
                'message': f'Excessive V2G power: {self.v2g_power:.1f} kW'
            })
        
        if anomalies:
            self.anomaly_count += 1
        
        return anomalies
    
    def detect_attack_pattern(self, anomalies):
        """Detect attack patterns"""
        attack_detected = False
        attack_type = None
        
        # Pattern 1: Sinusoidal V2G manipulation (grid destabilization target)
        if len(self.v2g_history) >= 10:
            v2g_list = list(self.v2g_history)[-10:]
            oscillation_count = sum(1 for i in range(1, len(v2g_list)) 
                                   if (v2g_list[i] > 0) != (v2g_list[i-1] > 0))
            if oscillation_count >= 4:
                attack_detected = True
                attack_type = "V2G_OSCILLATION_ATTACK"
                self.attack_indicators.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': attack_type,
                    'message': 'V2G power oscillation detected - Grid destabilization attack!'
                })
        
        # Pattern 2: Simultaneous high V2G
        critical_count = sum(1 for a in anomalies if a['level'] in [AlertLevel.CRITICAL, AlertLevel.ATTACK])
        if critical_count >= 2:
            attack_detected = True
            attack_type = "COORDINATED_DESTABILIZATION"
            self.attack_indicators.append({
                'timestamp': datetime.now().isoformat(),
                'type': attack_type,
                'message': 'Coordinated grid destabilization attack detected!'
            })
        
        return attack_detected, attack_type
    
    def print_status(self, anomalies=None):
        """Print status report"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine status
        if any(a['level'] == AlertLevel.ATTACK for a in (anomalies or [])):
            status_icon = "[!!!]"
            status_text = "ATTACK"
        elif any(a['level'] == AlertLevel.CRITICAL for a in (anomalies or [])):
            status_icon = "[!]"
            status_text = "CRITICAL"
        elif any(a['level'] == AlertLevel.WARNING for a in (anomalies or [])):
            status_icon = "[!]"
            status_text = "WARNING"
        else:
            status_icon = "[OK]"
            status_text = "NORMAL"
        
        print(f"\n{'='*70}")
        print(f"[{timestamp}] {status_icon} MICROGRID STATUS: {status_text}")
        print(f"{'='*70}")
        
        # Basic parameters
        freq_status = "[OK]" if abs(self.frequency - 50) < self.FREQ_TOLERANCE else "[!]"
        volt_status = "[OK]" if abs(self.voltage - 230) < self.VOLTAGE_TOLERANCE else "[!]"
        
        print(f"\n[GRID] GRID PARAMETERS:")
        print(f"   {freq_status} Frequency: {self.frequency:.2f} Hz (Nominal: {self.NOMINAL_FREQUENCY} Hz)")
        print(f"   {volt_status} Voltage: {self.voltage:.1f} V (Nominal: {self.NOMINAL_VOLTAGE} V)")
        print(f"   [>] Load: {self.total_load:.1f} kW")
        print(f"   [>] Generation: {self.total_generation:.1f} kW")
        print(f"   [>] V2G Total: {self.v2g_power:.1f} kW")
        
        # Connected EVs
        print(f"\n[EV] CONNECTED EVs ({len(self.connected_evs)}):")
        if self.connected_evs:
            for ev_id, ev_info in self.connected_evs.items():
                power = self.ev_v2g_power.get(ev_id, 0)
                mode = "V2G" if power > 0 else "IDLE"
                print(f"   - {ev_id}: {mode} ({power:.1f} kW)")
        else:
            print(f"   - No connected EVs")
        
        # Anomalies
        if anomalies:
            print(f"\n[ALERT] DETECTED ANOMALIES:")
            for a in anomalies:
                level_icon = {
                    AlertLevel.INFO: "[i]",
                    AlertLevel.WARNING: "[!]",
                    AlertLevel.CRITICAL: "[!!]",
                    AlertLevel.ATTACK: "[!!!]"
                }.get(a['level'], "[?]")
                print(f"   {level_icon} [{a['level'].value}] {a['message']}")
        
        # Attack indicators
        if self.attack_indicators:
            print(f"\n{'!'*50}")
            print(f"[!!!] ATTACK DETECTED!")
            for indicator in self.attack_indicators[-3:]:  # Last 3 indicators
                print(f"   - {indicator['type']}: {indicator['message']}")
            print(f"{'!'*50}")
        
        # Statistics
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"\n[STATS] STATISTICS:")
        print(f"   - Total Checks: {self.total_checks}")
        print(f"   - Anomaly Count: {self.anomaly_count}")
        print(f"   - Anomaly Rate: {anomaly_rate:.1f}%")
        
        print(f"{'='*70}\n")
    
    async def monitor(self, interval=2):
        """Monitoring loop"""
        logger.info("[START] Monitoring starting...\n")
        
        try:
            while True:
                # Simulate grid dynamics
                self.simulate_grid_dynamics()
                
                # Detect anomaly
                anomalies = self.detect_anomaly()
                
                # Check attack pattern
                attack_detected, attack_type = self.detect_attack_pattern(anomalies)
                
                # Print status
                self.print_status(anomalies)
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n[STOP] Monitoring stopped")
            self._print_summary()
    
    def _print_summary(self):
        """Summary report"""
        print(f"\n{'='*70}")
        print(f"[SUMMARY] SUMMARY REPORT")
        print(f"{'='*70}")
        print(f"   Total Checks: {self.total_checks}")
        print(f"   Detected Anomalies: {self.anomaly_count}")
        print(f"   Attack Indicators: {len(self.attack_indicators)}")
        anomaly_rate = (self.anomaly_count / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"   Anomaly Rate: {anomaly_rate:.1f}%")
        print(f"{'='*70}\n")


async def demo_attack_scenario(monitor):
    """Demo attack scenario"""
    await asyncio.sleep(5)
    
    logger.info("\n" + "="*50)
    logger.info("DEMO: Normal operation starting...")
    logger.info("="*50 + "\n")
    
    # Add normal EVs
    monitor.add_ev("EV_001", 11)
    monitor.add_ev("EV_002", 22)
    await asyncio.sleep(10)
    
    # Normal V2G
    monitor.update_v2g_power("EV_001", 5)
    await asyncio.sleep(10)
    
    logger.info("\n" + "!"*50)
    logger.info("DEMO: V2G Attack starting...")
    logger.info("!"*50 + "\n")
    
    # Attack: Multiple EVs coordinated discharge
    monitor.add_ev("EV_003", 11)
    monitor.add_ev("EV_004", 11)
    monitor.add_ev("EV_005", 11)
    
    await asyncio.sleep(3)
    
    # Sudden high V2G
    monitor.update_v2g_power("EV_001", 11)
    monitor.update_v2g_power("EV_002", 22)
    monitor.update_v2g_power("EV_003", 11)
    monitor.update_v2g_power("EV_004", 11)
    monitor.update_v2g_power("EV_005", 11)
    
    await asyncio.sleep(20)
    
    # V2G oscillation (grid destabilization attack)
    for i in range(10):
        if i % 2 == 0:
            monitor.update_v2g_power("EV_001", 11)
            monitor.update_v2g_power("EV_002", 22)
        else:
            monitor.update_v2g_power("EV_001", 0)
            monitor.update_v2g_power("EV_002", 0)
        await asyncio.sleep(3)


async def main():
    """Main program"""
    import sys
    
    monitor = MicrogridMonitor()
    
    # Demo mode?
    demo_mode = "--demo" in sys.argv
    
    if demo_mode:
        logger.info("[DEMO] DEMO MODE ACTIVE")
        tasks = [
            monitor.monitor(interval=2),
            demo_attack_scenario(monitor)
        ]
    else:
        # Simple simulation
        monitor.add_ev("EV_NORMAL_001", 11)
        monitor.update_v2g_power("EV_NORMAL_001", 5)
        tasks = [monitor.monitor(interval=3)]
    
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Program terminated")
