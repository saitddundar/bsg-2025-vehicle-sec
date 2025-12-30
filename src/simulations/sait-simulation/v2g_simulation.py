#!/usr/bin/env python3
"""
V2G Protocol Manipulation - Combined Simulation
Runs all components in a single terminal window.

This script:
1. Starts the CSMS server
2. Starts the microgrid monitor
3. Simulates a normal charging station
4. Executes the attack scenario
"""

import asyncio
import logging
import json
import random
import math
from datetime import datetime, timezone
from enum import Enum
from collections import deque

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] %(message)s'
)


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ATTACK = "ATTACK"


class MicrogridState:
    """Microgrid state"""
    def __init__(self):
        self.frequency = 50.0
        self.voltage = 230.0
        self.total_load = 100.0
        self.total_generation = 110.0
        self.v2g_power = 0.0
        self.connected_evs = {}
        self.energy_flows = {}
        self.alerts = []
        
        # Historical data
        self.freq_history = deque(maxlen=30)
        self.voltage_history = deque(maxlen=30)
        self.v2g_history = deque(maxlen=30)
        
        # Statistics
        self.total_checks = 0
        self.anomaly_count = 0
        self.attack_detected = False
    
    def add_ev(self, ev_id, mode='charging', power_kw=0):
        self.connected_evs[ev_id] = {
            'mode': mode,
            'power_kw': power_kw,
            'connected_at': datetime.now().strftime('%H:%M:%S')
        }
        self.energy_flows[ev_id] = power_kw
    
    def update_v2g(self, ev_id, power_kw):
        if ev_id in self.connected_evs:
            self.connected_evs[ev_id]['power_kw'] = power_kw
            self.connected_evs[ev_id]['mode'] = 'v2g' if power_kw > 0 else 'charging'
            self.energy_flows[ev_id] = power_kw
    
    def calculate_grid_state(self):
        """Calculate grid state"""
        self.v2g_power = sum(self.energy_flows.values())
        
        # Power balance
        power_balance = self.total_generation + self.v2g_power - self.total_load
        
        # Frequency (sensitive to power balance)
        freq_deviation = power_balance * 0.01
        noise = random.uniform(-0.05, 0.05)
        self.frequency = 50.0 + freq_deviation + noise
        
        # Voltage
        voltage_deviation = power_balance * 0.1
        noise = random.uniform(-1, 1)
        self.voltage = 230.0 + voltage_deviation + noise
        
        # Add to history
        self.freq_history.append(self.frequency)
        self.voltage_history.append(self.voltage)
        self.v2g_history.append(self.v2g_power)
    
    def detect_anomaly(self):
        """Detect anomaly"""
        self.total_checks += 1
        anomalies = []
        
        # Frequency control
        freq_dev = abs(self.frequency - 50.0)
        if freq_dev > 0.5:
            level = AlertLevel.WARNING if freq_dev < 1.0 else AlertLevel.CRITICAL
            anomalies.append({
                'type': 'FREQUENCY',
                'level': level,
                'value': f'{self.frequency:.2f} Hz',
                'message': f'Frequency deviation: {freq_dev:.2f} Hz'
            })
        
        # Voltage control
        volt_dev = abs(self.voltage - 230.0)
        if volt_dev > 23:
            level = AlertLevel.WARNING if volt_dev < 30 else AlertLevel.CRITICAL
            anomalies.append({
                'type': 'VOLTAGE',
                'level': level,
                'value': f'{self.voltage:.1f} V',
                'message': f'Voltage deviation: {volt_dev:.1f} V'
            })
        
        # Rapid V2G change
        if len(self.v2g_history) >= 3:
            recent = list(self.v2g_history)[-3:]
            change = max(recent) - min(recent)
            if change > 20:
                anomalies.append({
                    'type': 'RAPID_V2G',
                    'level': AlertLevel.WARNING,
                    'value': f'{change:.1f} kW',
                    'message': f'Rapid V2G change: {change:.1f} kW'
                })
        
        # Coordinated attack
        active_v2g = sum(1 for p in self.energy_flows.values() if p > 5)
        if active_v2g >= 3 and self.v2g_power > 30:
            anomalies.append({
                'type': 'COORDINATED',
                'level': AlertLevel.ATTACK,
                'value': f'{active_v2g} EV',
                'message': f'Coordinated V2G: {active_v2g} EVs, {self.v2g_power:.1f} kW'
            })
            self.attack_detected = True
        
        # Excessive V2G
        if self.v2g_power > 50:
            anomalies.append({
                'type': 'EXCESSIVE_V2G',
                'level': AlertLevel.CRITICAL,
                'value': f'{self.v2g_power:.1f} kW',
                'message': f'Excessive V2G power!'
            })
        
        if anomalies:
            self.anomaly_count += 1
            self.alerts.extend(anomalies)
        
        return anomalies


def print_banner():
    """Header banner"""
    print("\n" + "="*70)
    print("""
    [V] [2] [G]    [S] [I] [M]
    
    V2G Protocol Manipulation Simulation
    Microgrid Destabilization Attack Demo
    """)
    print("="*70)



def print_grid_status(grid: MicrogridState, anomalies=None):
    """Print grid status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Status determination
    if grid.attack_detected:
        status = "[ATTACK] ATTACK DETECTED"
        line_char = "!"
    elif any(a['level'] == AlertLevel.CRITICAL for a in (anomalies or [])):
        status = "[CRITICAL] CRITICAL"
        line_char = "*"
    elif any(a['level'] == AlertLevel.WARNING for a in (anomalies or [])):
        status = "[WARNING] WARNING"
        line_char = "-"
    else:
        status = "[OK] NORMAL"
        line_char = "_"
    
    print(f"\n{line_char*35}")
    print(f"[{timestamp}] {status}")
    print(f"{line_char*35}")
    
    # Grid parameters
    freq_icon = "[OK]" if abs(grid.frequency - 50) < 0.5 else "[!]"
    volt_icon = "[OK]" if abs(grid.voltage - 230) < 23 else "[!]"
    
    print(f"\n[GRID] GRID:")
    print(f"   {freq_icon} Frequency: {grid.frequency:.2f} Hz")
    print(f"   {volt_icon} Voltage: {grid.voltage:.1f} V")
    print(f"   [>>] Load: {grid.total_load:.0f} kW | Generation: {grid.total_generation:.0f} kW")
    print(f"   [>>] V2G: {grid.v2g_power:.1f} kW")
    
    # Connected EVs
    print(f"\n[EV] EVs ({len(grid.connected_evs)}):")
    for ev_id, info in grid.connected_evs.items():
        mode_icon = "[V2G]" if info['mode'] == 'v2g' else "[CHG]"
        print(f"   {mode_icon} {ev_id}: {info['power_kw']:.1f} kW ({info['mode']})")
    
    # Anomalies
    if anomalies:
        print(f"\n[ALERT] ANOMALIES:")
        for a in anomalies:
            icons = {
                AlertLevel.INFO: "[i]",
                AlertLevel.WARNING: "[!]",
                AlertLevel.CRITICAL: "[!!]",
                AlertLevel.ATTACK: "[!!!]"
            }
            print(f"   {icons.get(a['level'], '[?]')} {a['message']}")
    
    # Statistics
    if grid.total_checks > 0:
        rate = (grid.anomaly_count / grid.total_checks) * 100
        print(f"\n[STATS] Check: {grid.total_checks} | Anomaly: {grid.anomaly_count} ({rate:.0f}%)")


async def normal_operation_phase(grid: MicrogridState, duration_sec=15):
    """Normal operation phase"""
    print("\n" + "="*70)
    print("[PHASE 1] PHASE 1: NORMAL OPERATION")
    print("="*70)
    
    # Add normal EVs
    grid.add_ev("EV_001", mode='charging', power_kw=0)
    grid.add_ev("EV_002", mode='charging', power_kw=0)
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Normal charging simulation
        grid.update_v2g("EV_001", random.uniform(-11, -7))  # Negative = charging
        grid.update_v2g("EV_002", random.uniform(-22, -18))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


async def v2g_phase(grid: MicrogridState, duration_sec=15):
    """Normal V2G phase"""
    print("\n" + "="*70)
    print("[PHASE 2] PHASE 2: NORMAL V2G OPERATION")
    print("="*70)
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Normal V2G (low power)
        grid.update_v2g("EV_001", random.uniform(3, 7))
        grid.update_v2g("EV_002", random.uniform(5, 10))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


async def attack_phase(grid: MicrogridState, duration_sec=20):
    """Attack phase"""
    print("\n" + "!"*35)
    print("[PHASE 3] PHASE 3: V2G PROTOCOL MANIPULATION ATTACK")
    print("!"*35)
    print("\n[ATTACK] Attacker injecting fake V2G commands...")
    print("[ATTACK] Multiple 'fake EVs' initiating coordinated discharge...\n")
    
    # Attack: Add multiple fake EVs
    grid.add_ev("MALICIOUS_001", mode='v2g', power_kw=11)
    grid.add_ev("MALICIOUS_002", mode='v2g', power_kw=11)
    grid.add_ev("MALICIOUS_003", mode='v2g', power_kw=11)
    
    start = asyncio.get_event_loop().time()
    phase = 0
    
    while asyncio.get_event_loop().time() - start < duration_sec:
        phase += 1
        
        if phase % 3 == 0:
            # Oscillation attack
            print("\n[ALERT] [ATTACK] V2G Oscillation - Targeted grid instability!")
            for ev_id in grid.connected_evs:
                if "MALICIOUS" in ev_id:
                    power = 15 if phase % 6 == 0 else 0
                    grid.update_v2g(ev_id, power)
        else:
            # Coordinated high power
            for ev_id in grid.connected_evs:
                if "MALICIOUS" in ev_id:
                    grid.update_v2g(ev_id, random.uniform(10, 15))
        
        # Legitimate EVs also affected
        grid.update_v2g("EV_001", random.uniform(8, 12))
        grid.update_v2g("EV_002", random.uniform(15, 22))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(2)


async def mitigation_phase(grid: MicrogridState, duration_sec=10):
    """Mitigation phase"""
    print("\n" + "="*70)
    print("[PHASE 4] PHASE 4: MITIGATION - Blocking Attack")
    print("="*70)
    print("\n[GUARD] Anomaly detection system active!")
    print("[GUARD] Isolating malicious EVs...\n")
    
    # Remove malicious EVs
    await asyncio.sleep(2)
    for ev_id in list(grid.connected_evs.keys()):
        if "MALICIOUS" in ev_id:
            print(f"   [BLOCKED] {ev_id} connection terminated...")
            del grid.connected_evs[ev_id]
            del grid.energy_flows[ev_id]
            await asyncio.sleep(1)
    
    grid.attack_detected = False
    
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration_sec:
        # Return to normal operation
        grid.update_v2g("EV_001", random.uniform(3, 6))
        grid.update_v2g("EV_002", random.uniform(5, 8))
        
        grid.calculate_grid_state()
        anomalies = grid.detect_anomaly()
        print_grid_status(grid, anomalies)
        
        await asyncio.sleep(3)


def print_summary(grid: MicrogridState):
    """Summary report"""
    print("\n" + "="*70)
    print("[SUMMARY] SIMULATION SUMMARY")
    print("="*70)
    print(f"""
    Total Check: {grid.total_checks}
    Detected Anomaly: {grid.anomaly_count}
    Anomaly Rate: {(grid.anomaly_count/grid.total_checks*100):.1f}%
    
    Attack Scenario: V2G Protocol Manipulation
    Target: Microgrid Destabilization
    
    Attack Methods:
    - Fake V2G Command Injection
    - Coordinated Multi-EV Discharge
    - V2G Power Oscillation
    
    Detection Methods:
    - Frequency/Voltage Monitoring
    - Rapid V2G Change Detection
    - Coordinated Attack Pattern Analysis
    """)
    print("="*70)


async def main():
    """Main simulation"""
    print_banner()
    
    print("\n[INIT] Simulation starting...")
    print("   This demo consists of 4 phases:")
    print("   1. Normal Operation (charging)")
    print("   2. Normal V2G (vehicle to grid)")
    print("   3. ATTACK (protocol manipulation)")
    print("   4. Mitigation (attack blocking)")
    print("\n   Press Ctrl+C to stop.\n")
    
    await asyncio.sleep(3)
    
    grid = MicrogridState()
    
    try:
        # Phase 1: Normal operation
        await normal_operation_phase(grid, duration_sec=12)
        
        # Phase 2: Normal V2G
        await v2g_phase(grid, duration_sec=12)
        
        # Phase 3: Attack
        await attack_phase(grid, duration_sec=18)
        
        # Phase 4: Mitigation
        await mitigation_phase(grid, duration_sec=10)
        
        print_summary(grid)
        
    except KeyboardInterrupt:
        print("\n\n[EXIT] Simulation stopped")
        print_summary(grid)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[EXIT] Program terminated")
