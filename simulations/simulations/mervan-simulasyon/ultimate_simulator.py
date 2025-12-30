"""
ULTIMATE EVSE P-DoS SIMULATOR
Tam fonksiyonel, görsel olarak muhteşem, gerçek simülasyon
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import json
import random
import os
from collections import deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultimate-evse-simulator-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class LogManager:
    """Kapsamlı log yönetimi"""
    def __init__(self):
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log dosyaları
        self.main_log = os.path.join(self.log_dir, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.can_log = os.path.join(self.log_dir, "can_bus.log")
        self.ocpp_log = os.path.join(self.log_dir, "ocpp.log")
        self.gps_log = os.path.join(self.log_dir, "gps.log")
        self.attack_log = os.path.join(self.log_dir, "attack.log")
        
        # Real-time log buffer (son 500 satır)
        self.terminal_buffer = deque(maxlen=500)
        
    def log(self, category, level, message, data=None):
        """Merkezi loglama"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'category': category,
            'level': level,
            'message': message,
            'data': data
        }
        
        # Terminal buffer
        self.terminal_buffer.append(log_entry)
        
        # Dosya yazma
        log_line = f"[{timestamp}] [{category}] [{level}] {message}"
        if data:
            log_line += f" | Data: {json.dumps(data)}"
        log_line += "\n"
        
        # Ana log
        with open(self.main_log, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # Kategori bazlı log
        category_log_map = {
            'CAN': self.can_log,
            'OCPP': self.ocpp_log,
            'GPS': self.gps_log,
            'ATTACK': self.attack_log
        }
        
        if category in category_log_map:
            with open(category_log_map[category], 'a', encoding='utf-8') as f:
                f.write(log_line)
        
        # WebSocket'e gönder
        socketio.emit('terminal_output', log_entry)
        
        return log_entry

class CANBusSimulator:
    """Gerçek CAN bus simülasyonu"""
    def __init__(self, log_manager):
        self.log = log_manager
        self.mode = 'normal'  # normal, charging, dos_attack
        self.bus_load = 15
        self.error_count = 0
        self.blocked_count = 0
        self.message_count = 0
        
        # CAN ID'ler
        self.CAN_IDS = {
            '0x000': {'name': 'MALICIOUS', 'priority': 'MAXIMUM', 'ecu': 'Attacker'},
            '0x100': {'name': 'SPEED', 'priority': 'HIGH', 'ecu': 'ABS'},
            '0x1F0': {'name': 'BMS', 'priority': 'HIGH', 'ecu': 'BMS'},
            '0x200': {'name': 'GEAR', 'priority': 'NORMAL', 'ecu': 'TCM'},
            '0x250': {'name': 'ENGINE', 'priority': 'NORMAL', 'ecu': 'ECM'},
            '0x300': {'name': 'HVAC', 'priority': 'LOW', 'ecu': 'HVAC'},
        }
        
    def generate_normal_traffic(self):
        """Normal CAN trafiği"""
        messages = []
        
        # BMS mesajı
        soc = random.randint(80, 90)
        temp = random.randint(23, 27)
        data = [soc, 0x00, temp, 0x00, 0x00, 0x00, 0x00, 0x00]
        messages.append({
            'id': '0x1F0',
            'dlc': 8,
            'data': data,
            'status': 'TX',
            'blocked': False
        })
        
        # Speed mesajı
        speed = 0
        data = [0x00, speed, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        messages.append({
            'id': '0x100',
            'dlc': 8,
            'data': data,
            'status': 'TX',
            'blocked': False
        })
        
        # Gear mesajı
        data = [0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # P
        messages.append({
            'id': '0x200',
            'dlc': 8,
            'data': data,
            'status': 'TX',
            'blocked': False
        })
        
        self.bus_load = random.randint(12, 18)
        self.message_count += len(messages)
        
        for msg in messages:
            self.log.log('CAN', 'INFO', 
                f"TX: ID={msg['id']} DLC={msg['dlc']} Data={msg['data']}", 
                {'message': msg})
        
        return messages
    
    def generate_dos_attack(self):
        """CAN DoS saldırısı"""
        messages = []
        
        # 0x000 ID flood (10 mesaj)
        for i in range(10):
            data = [0x00] * 8
            messages.append({
                'id': '0x000',
                'dlc': 8,
                'data': data,
                'status': 'TX',
                'blocked': False,
                'malicious': True
            })
            
            self.log.log('CAN', 'CRITICAL', 
                f"ATTACK: 0x000 FLOOD #{i+1} - Arbitration Lock Active",
                {'id': '0x000', 'priority': 'MAXIMUM'})
        
        # Normal ECU'lar bloke ediliyor
        blocked_ecus = ['0x1F0', '0x100', '0x200', '0x250', '0x300']
        for can_id in blocked_ecus:
            data = [0xFF] * 8
            messages.append({
                'id': can_id,
                'dlc': 8,
                'data': data,
                'status': 'BLOCKED',
                'blocked': True,
                'malicious': False
            })
            
            self.blocked_count += 1
            ecu_name = self.CAN_IDS[can_id]['ecu']
            
            self.log.log('CAN', 'ERROR', 
                f"BLOCKED: {ecu_name} (ID={can_id}) - Arbitration Lost",
                {'id': can_id, 'ecu': ecu_name, 'reason': 'Arbitration Lost to 0x000'})
        
        self.bus_load = 98
        self.error_count = 999
        self.message_count += len(messages)
        
        return messages

class GPSSimulator:
    """GPS ve telemetri simülasyonu - Gerçek fizik modeli"""
    def __init__(self, log_manager):
        self.log = log_manager
        self.mode = 'stationary'  # stationary, moving, anomaly
        self.lat = 41.0082
        self.lon = 28.9784
        self.speed = 0
        self.soc = 85
        
        # Fizik parametreleri
        self.target_speed = 0
        self.acceleration = 2.5  # m/s² (normal araç)
        self.deceleration = 4.0  # m/s² (fren)
        self.max_speed = 120  # km/h
        
        # Anomali için
        self.attack_transition_phase = 0  # 0: normal, 1: hızlanma, 2: devam
        self.attack_started = False
        
    def update(self):
        """GPS güncelle - Gerçek fizik ile"""
        if self.mode == 'stationary':
            # Normal şarj - hız sıfırdan farklılaşmasın
            self.speed = max(0, self.speed - 1)  # Yavaş yavaş dur
            self.soc = min(100, self.soc + 0.5)
            
            self.log.log('GPS', 'INFO', 
                f"Vehicle stationary at ({self.lat:.6f}, {self.lon:.6f}), SoC: {self.soc:.1f}%",
                {'lat': self.lat, 'lon': self.lon, 'speed': 0, 'soc': self.soc})
        
        elif self.mode == 'moving':
            # Gerçekçi hareket - ivme ile
            self.target_speed = random.randint(60, 80)
            
            if self.speed < self.target_speed:
                # İvmelenme: km/h → m/s → km/h
                delta_v = self.acceleration * 0.5 * 3.6  # 0.5s için km/h
                self.speed = min(self.target_speed, self.speed + delta_v)
            elif self.speed > self.target_speed:
                # Yavaşlama
                delta_v = self.deceleration * 0.5 * 3.6
                self.speed = max(self.target_speed, self.speed - delta_v)
            
            # Konum güncelle (gerçek hesaplama)
            # 1° latitude = 111.32 km
            # speed (km/h) * 0.5s = speed * 0.5 / 3600 = speed / 7200 km
            distance_km = self.speed / 7200  # 0.5 saniyede gidilen mesafe
            self.lat += (distance_km / 111.32)
            self.lon += (distance_km / (111.32 * 0.74))  # İstanbul enlem düzeltmesi
            
            self.soc = max(0, self.soc - 0.15)
            
            self.log.log('GPS', 'INFO', 
                f"Vehicle moving at {self.speed:.1f} km/h, Location: ({self.lat:.6f}, {self.lon:.6f}), SoC: {self.soc:.1f}%",
                {'lat': self.lat, 'lon': self.lon, 'speed': self.speed, 'soc': self.soc})
        
        elif self.mode == 'anomaly':
            # FİZİKSEL OLARAK İMKANSIZ: Hareket ederken şarj
            # AMA gerçekçi ivmelenme göster
            
            if not self.attack_started:
                self.attack_started = True
                self.attack_transition_phase = 0
                self.log.log('GPS', 'WARNING', 
                    "GPS DATA MANIPULATION DETECTED: Injecting false speed data",
                    {'attack': 'GPS spoofing', 'method': 'CAN injection'})
            
            # Faz 1: Yavaş yavaş hızlan (0 → 30 km/h) - 3 güncelleme
            if self.attack_transition_phase < 3:
                delta_v = self.acceleration * 0.5 * 3.6  # 2.5 m/s² = 9 km/h per update
                self.speed = min(30, self.speed + delta_v)
                self.attack_transition_phase += 1
                
                self.log.log('GPS', 'WARNING', 
                    f"SPEED MANIPULATION: Injecting false speed {self.speed:.1f} km/h (Phase {self.attack_transition_phase}/3)",
                    {'lat': self.lat, 'lon': self.lon, 'speed': self.speed, 'phase': 'acceleration'})
            
            # Faz 2: Orta hıza çık (30 → 60 km/h) - 3 güncelleme
            elif self.attack_transition_phase < 6:
                delta_v = self.acceleration * 0.5 * 3.6
                self.speed = min(60, self.speed + delta_v)
                self.attack_transition_phase += 1
                
                self.log.log('GPS', 'ERROR', 
                    f"ANOMALY ESCALATING: Vehicle shows {self.speed:.1f} km/h but still charging! (Phase {self.attack_transition_phase-3}/3)",
                    {'lat': self.lat, 'lon': self.lon, 'speed': self.speed, 'soc': self.soc, 'phase': 'escalation'})
            
            # Faz 3: Yüksek hıza çık (60 → 90 km/h) - devam
            else:
                # Random varyasyon (75-95 km/h arası)
                noise = random.uniform(-5, 5)
                target_speed = 85 + noise
                
                if self.speed < target_speed:
                    delta_v = self.acceleration * 0.5 * 3.6 * 0.5  # Daha yavaş ivme
                    self.speed = min(target_speed, self.speed + delta_v)
                elif self.speed > target_speed:
                    delta_v = 2.0 * 0.5 * 3.6 * 0.5
                    self.speed = max(target_speed, self.speed - delta_v)
                
                self.log.log('GPS', 'CRITICAL', 
                    f"CRITICAL ANOMALY: Vehicle moving at {self.speed:.1f} km/h but charging! SoC: {self.soc:.1f}% (IMPOSSIBLE)",
                    {'lat': self.lat, 'lon': self.lon, 'speed': self.speed, 'soc': self.soc, 'anomaly': True, 'phase': 'sustained'})
            
            # Konum güncelle (sahte hareket)
            distance_km = self.speed / 7200
            self.lat += (distance_km / 111.32)
            self.lon += (distance_km / (111.32 * 0.74))
            
            # SoC artıyor (fiziksel olarak imkansız!)
            self.soc = min(100, self.soc + 0.5)
        
        return {
            'lat': self.lat,
            'lon': self.lon,
            'speed': self.speed,
            'soc': self.soc,
            'mode': self.mode
        }

class OCPPSimulator:
    """OCPP protokol simülasyonu"""
    def __init__(self, log_manager):
        self.log = log_manager
        self.evse_id = "EVSE-001"
        self.session_id = None
        self.compromised = False
        
    def send_heartbeat(self):
        """Heartbeat gönder"""
        self.log.log('OCPP', 'INFO', 
            f"TX → CSMS: Heartbeat from {self.evse_id}",
            {'message_type': 'Heartbeat', 'evse_id': self.evse_id})
    
    def send_meter_values(self, soc, power):
        """Meter values gönder"""
        self.log.log('OCPP', 'INFO', 
            f"TX → CSMS: MeterValues - SoC: {soc}%, Power: {power} kW",
            {'message_type': 'MeterValues', 'soc': soc, 'power': power})
    
    def receive_firmware_update(self, url):
        """Firmware update al"""
        if not self.compromised:
            self.log.log('OCPP', 'WARNING', 
                f"RX ← CSMS: UpdateFirmware - URL: {url}",
                {'message_type': 'UpdateFirmware', 'url': url})
        else:
            malicious_url = "https://malicious-c2-server.onion/rootkit.bin"
            self.log.log('OCPP', 'CRITICAL', 
                f"RX ← ATTACKER (MitM): UpdateFirmware - MALICIOUS URL: {malicious_url}",
                {'message_type': 'UpdateFirmware', 'url': malicious_url, 'attack': 'MitM'})

class AttackSimulator:
    """Saldırı simülasyonu"""
    def __init__(self, log_manager, can_sim, gps_sim, ocpp_sim):
        self.log = log_manager
        self.can = can_sim
        self.gps = gps_sim
        self.ocpp = ocpp_sim
        
        self.current_stage = 0
        self.running = False
        
        self.vehicle_state = {
            'speed': 0,
            'rpm': 0,
            'battery_soc': 85,
            'battery_temp': 25,
            'motor_temp': 25,
            'gear': 'P',
            'warnings': {
                'check_engine': False,
                'abs': False,
                'airbag': False,
                'battery': False,
                'traction': False,
                'oil': False
            },
            'dtc_codes': []
        }
        
        self.evse_state = {
            'status': 'IDLE',
            'power': 0,
            'voltage': 400,
            'current': 0,
            'energy': 0,
            'temperature': 30,
            'firmware': 'v1.2.4',
            'compromised': False
        }
        
        self.stages = [
            {'id': 0, 'name': 'Normal Şarj', 'duration': 20, 'color': 'success'},
            {'id': 1, 'name': 'ARP Spoofing & MitM', 'duration': 15, 'color': 'warning'},
            {'id': 2, 'name': 'Firmware Manipulation', 'duration': 15, 'color': 'danger'},
            {'id': 3, 'name': 'CAN Bus DoS Attack', 'duration': 15, 'color': 'danger'},
            {'id': 4, 'name': 'Hard Brick - P-DoS', 'duration': 15, 'color': 'dark'}
        ]
    
    def stage_0_normal(self):
        """Faz 0: Normal şarj"""
        self.evse_state['status'] = 'CHARGING'
        
        # Gerçek elektrik hesaplamaları: P = V * I
        # AC Charging: 230V veya 400V (3-phase)
        # DC Fast Charging: 400V-800V
        self.evse_state['voltage'] = 400  # DC voltage
        
        # Power ramp up (gerçekçi şarj başlangıcı)
        # İlk 10 saniye: 0 → 7.4 kW (yavaş başlama)
        if not hasattr(self, 'charge_start_time'):
            self.charge_start_time = time.time()
        
        elapsed = time.time() - self.charge_start_time
        if elapsed < 10:
            # Ramp up: 0 → 7.4 kW in 10 seconds
            self.evse_state['power'] = min(7.4, elapsed * 0.74)
        else:
            # Normal şarj: 7.4 kW (slightly varying)
            self.evse_state['power'] = 7.4 + random.uniform(-0.2, 0.2)
        
        # I = P / V (Ampere hesaplama)
        self.evse_state['current'] = (self.evse_state['power'] * 1000) / self.evse_state['voltage']
        
        # Enerji hesaplama: E = P * t (kWh)
        # 0.5 saniyede: power * (0.5/3600) kWh
        self.evse_state['energy'] += self.evse_state['power'] * (0.5 / 3600)
        
        # Sıcaklık artışı (gerçekçi ısınma)
        # Q = I²R (Joule heating)
        base_temp = 30
        current_heating = (self.evse_state['current'] ** 2) * 0.01  # Simplified
        self.evse_state['temperature'] = base_temp + current_heating + random.uniform(-0.5, 0.5)
        
        self.vehicle_state['battery_soc'] = min(100, self.vehicle_state['battery_soc'] + 0.3)
        self.vehicle_state['speed'] = 0
        self.vehicle_state['rpm'] = 0
        self.vehicle_state['gear'] = 'P'
        
        self.can.mode = 'normal'
        self.gps.mode = 'stationary'
        
        # OCPP mesajları
        if random.random() < 0.3:
            self.ocpp.send_heartbeat()
        
        if random.random() < 0.2:
            self.ocpp.send_meter_values(self.vehicle_state['battery_soc'], self.evse_state['power'])
        
        # CAN trafiği
        can_messages = self.can.generate_normal_traffic()
        
        # GPS güncelle
        gps_data = self.gps.update()
        
        self.log.log('SIMULATION', 'INFO', 
            f"Stage 0: Normal charging - SoC: {self.vehicle_state['battery_soc']:.1f}%, Power: {self.evse_state['power']} kW",
            {'stage': 0, 'vehicle': self.vehicle_state, 'evse': self.evse_state})
    
    def stage_1_mitm(self):
        """Faz 1: MitM saldırısı"""
        self.evse_state['status'] = 'UPDATING'
        
        self.log.log('ATTACK', 'WARNING', 
            "Stage 1 START: Initiating Man-in-the-Middle attack",
            {'stage': 1, 'attack_type': 'MitM'})
        
        # ARP Spoofing
        time.sleep(0.5)
        self.log.log('ATTACK', 'CRITICAL', 
            "ARP SPOOFING: Attacker MAC: DE:AD:BE:EF:13:37 → Target: EVSE (192.168.1.100)",
            {'attack': 'ARP Spoofing', 'attacker_mac': 'DE:AD:BE:EF:13:37', 'target_ip': '192.168.1.100'})
        
        # Legitimate OCPP request
        time.sleep(0.5)
        legitimate_url = "https://legitimate-csms.com/firmware/v1.2.5.bin"
        self.log.log('OCPP', 'INFO', 
            f"CSMS → EVSE: Legitimate UpdateFirmware request - URL: {legitimate_url}",
            {'source': 'CSMS', 'url': legitimate_url})
        
        # MitM interception
        time.sleep(0.5)
        self.log.log('ATTACK', 'CRITICAL', 
            "MITM INTERCEPTION: Legitimate request intercepted and modified",
            {'attack': 'MitM', 'action': 'URL Manipulation'})
        
        # Malicious URL injection
        time.sleep(0.5)
        malicious_url = "https://malicious-c2-server.onion/rootkit.bin"
        self.ocpp.receive_firmware_update(malicious_url)
        self.ocpp.compromised = True
        
        self.log.log('ATTACK', 'CRITICAL', 
            f"MALICIOUS PAYLOAD: Firmware URL replaced with: {malicious_url}",
            {'attack': 'Firmware Injection', 'url': malicious_url})
    
    def stage_2_firmware(self):
        """Faz 2: Firmware manipülasyonu"""
        self.evse_state['status'] = 'COMPROMISED'
        self.evse_state['compromised'] = True
        self.evse_state['firmware'] = 'v1.2.5 [ROOTKIT]'
        
        self.log.log('ATTACK', 'CRITICAL', 
            "Stage 2 START: Firmware manipulation and rootkit installation",
            {'stage': 2, 'attack_type': 'Firmware Manipulation'})
        
        # Rootkit installation
        time.sleep(0.5)
        self.log.log('ATTACK', 'CRITICAL', 
            "ROOTKIT INSTALLED: /lib/systemd/system-evse-daemon (Persistent backdoor)",
            {'attack': 'Rootkit', 'path': '/lib/systemd/system-evse-daemon', 'persistence': True})
        
        # Zombie EVSE
        time.sleep(0.5)
        self.log.log('ATTACK', 'CRITICAL', 
            "ZOMBIE EVSE: Device now under attacker control - Sending beacon to C2",
            {'attack': 'Zombie', 'c2_server': 'malicious-c2-server.onion', 'status': 'connected'})
        
        # Fake confirmation
        time.sleep(0.5)
        self.log.log('OCPP', 'WARNING', 
            "EVSE → CSMS: FirmwareStatusNotification: Installed (FALSE - Rootkit active)",
            {'message_type': 'FirmwareStatusNotification', 'status': 'Installed', 'actual': 'Rootkit Active'})
        
        # C2 commands
        time.sleep(0.5)
        self.log.log('ATTACK', 'CRITICAL', 
            "C2 COMMAND RECEIVED: Weaponize EVSE - Prepare CAN bus attack on next vehicle connection",
            {'c2_command': 'weaponize', 'target': 'CAN bus', 'trigger': 'next_vehicle'})
    
    def stage_3_can_dos(self):
        """Faz 3: CAN DoS saldırısı"""
        self.evse_state['status'] = 'ATTACKING'
        self.can.mode = 'dos_attack'
        
        self.log.log('ATTACK', 'CRITICAL', 
            "Stage 3 START: CAN bus DoS attack - 0x000 ID arbitration lock",
            {'stage': 3, 'attack_type': 'CAN DoS', 'method': '0x000 Priority Flood'})
        
        # Vehicle connection
        time.sleep(0.5)
        self.log.log('ATTACK', 'WARNING', 
            "VEHICLE CONNECTED: Rootkit activated - Accessing CAN transceiver via charging cable",
            {'vehicle_connected': True, 'can_access': 'via_charging_cable'})
        
        # CAN DoS attack
        time.sleep(0.5)
        can_messages = self.can.generate_dos_attack()
        
        # GPS anomaly (sahte hız verileri)
        self.gps.mode = 'anomaly'
        gps_data = self.gps.update()
        
        # Araç sensörleri de manipüle ediliyor
        # Gerçek fizik: RPM = (speed * gear_ratio * final_drive) / (tire_circumference / 60)
        # Simplified: RPM ≈ speed * 50 (for typical EV at highway speed)
        if gps_data['speed'] > 0:
            # Sahte RPM (motor çalışıyor gibi göster)
            target_rpm = int(gps_data['speed'] * 45)  # ~3600 RPM at 80 km/h
            
            # Gradual RPM change (gerçekçi)
            if self.vehicle_state['rpm'] < target_rpm:
                self.vehicle_state['rpm'] = min(target_rpm, self.vehicle_state['rpm'] + 200)
            
            # Motor sıcaklığı artıyor (sahte)
            self.vehicle_state['motor_temp'] = min(95, self.vehicle_state['motor_temp'] + 2)
        
        self.log.log('ATTACK', 'CRITICAL', 
            f"CAN BUS OVERLOAD: Bus load {self.can.bus_load}% - {self.can.blocked_count} ECUs blocked",
            {'bus_load': self.can.bus_load, 'blocked_ecus': self.can.blocked_count, 'attack_active': True})
    
    def stage_4_hard_brick(self):
        """Faz 4: Hard Brick"""
        self.evse_state['status'] = 'BRICKED'
        
        self.log.log('ATTACK', 'CRITICAL', 
            "Stage 4 START: Hard Brick - Permanent Denial of Service (P-DoS)",
            {'stage': 4, 'attack_type': 'P-DoS', 'severity': 'CRITICAL'})
        
        # Tüm uyarılar
        self.vehicle_state['warnings'] = {
            'check_engine': True,
            'abs': True,
            'airbag': True,
            'battery': True,
            'traction': True,
            'oil': True
        }
        
        # DTC kodları
        dtc_codes = [
            {'code': 'U0100', 'desc': 'Lost Communication With ECM/PCM', 'severity': 'CRITICAL'},
            {'code': 'U0121', 'desc': 'Lost Communication With ABS Control Module', 'severity': 'CRITICAL'},
            {'code': 'U0155', 'desc': 'Lost Communication With Battery Management System', 'severity': 'CRITICAL'},
            {'code': 'U0164', 'desc': 'Lost Communication With HVAC Control Module', 'severity': 'HIGH'},
            {'code': 'U0195', 'desc': 'Lost Communication With Transmission Control Module', 'severity': 'CRITICAL'},
        ]
        
        for dtc in dtc_codes:
            time.sleep(0.3)
            self.vehicle_state['dtc_codes'].append(dtc)
            self.log.log('VEHICLE', 'CRITICAL', 
                f"DTC GENERATED: {dtc['code']} - {dtc['desc']}",
                {'dtc': dtc['code'], 'description': dtc['desc'], 'severity': dtc['severity']})
        
        # Final status
        time.sleep(1)
        self.log.log('ATTACK', 'CRITICAL', 
            "HARD BRICK COMPLETE: Vehicle inoperable - Requires physical intervention",
            {'status': 'BRICKED', 'dtc_count': len(dtc_codes), 'recovery': 'Physical service required'})
        
        self.log.log('ATTACK', 'CRITICAL', 
            "P-DoS SUCCESSFUL: Permanent damage inflicted - Attack demonstration complete",
            {'attack_complete': True, 'damage': 'Permanent', 'cost': 'High'})
    
    def run_simulation(self):
        """Simülasyonu çalıştır"""
        self.running = True
        
        self.log.log('SIMULATION', 'INFO', 
            "=== EVSE P-DoS SIMULATION STARTED ===",
            {'total_stages': len(self.stages)})
        
        for stage_info in self.stages:
            if not self.running:
                break
            
            self.current_stage = stage_info['id']
            stage_start = time.time()
            
            # Stage başlangıcı
            socketio.emit('stage_change', {
                'stage': stage_info['id'],
                'name': stage_info['name'],
                'color': stage_info['color'],
                'duration': stage_info['duration']
            })
            
            self.log.log('SIMULATION', 'INFO', 
                f">>> STAGE {stage_info['id']}: {stage_info['name']} <<<",
                {'stage': stage_info['id'], 'duration': stage_info['duration']})
            
            # Stage execution
            while time.time() - stage_start < stage_info['duration']:
                if not self.running:
                    break
                
                if stage_info['id'] == 0:
                    self.stage_0_normal()
                elif stage_info['id'] == 1:
                    self.stage_1_mitm()
                    time.sleep(2)  # MitM adımları arası bekleme
                elif stage_info['id'] == 2:
                    self.stage_2_firmware()
                    time.sleep(2)
                elif stage_info['id'] == 3:
                    self.stage_3_can_dos()
                    time.sleep(1)
                elif stage_info['id'] == 4:
                    self.stage_4_hard_brick()
                    break  # Son stage
                
                # State update
                socketio.emit('state_update', {
                    'vehicle': self.vehicle_state,
                    'evse': self.evse_state,
                    'can': {
                        'mode': self.can.mode,
                        'bus_load': self.can.bus_load,
                        'errors': self.can.error_count,
                        'blocked': self.can.blocked_count
                    },
                    'gps': self.gps.update()
                })
                
                time.sleep(0.5)
        
        self.log.log('SIMULATION', 'INFO', 
            "=== EVSE P-DoS SIMULATION COMPLETED ===",
            {'stages_completed': len(self.stages)})
        
        self.running = False
    
    def reset(self):
        """Simülasyonu sıfırla"""
        self.running = False
        self.__init__(self.log, self.can, self.gps, self.ocpp)

# Global instances
log_manager = LogManager()
can_simulator = CANBusSimulator(log_manager)
gps_simulator = GPSSimulator(log_manager)
ocpp_simulator = OCPPSimulator(log_manager)
attack_simulator = AttackSimulator(log_manager, can_simulator, gps_simulator, ocpp_simulator)

@app.route('/')
def index():
    return render_template('ultimate_simulator.html')

@app.route('/api/logs')
def get_logs():
    """Log'ları al"""
    return jsonify(list(log_manager.terminal_buffer))

@app.route('/api/download_log/<log_type>')
def download_log(log_type):
    """Log dosyasını indir"""
    log_files = {
        'main': log_manager.main_log,
        'can': log_manager.can_log,
        'ocpp': log_manager.ocpp_log,
        'gps': log_manager.gps_log,
        'attack': log_manager.attack_log
    }
    
    if log_type in log_files:
        from flask import send_file
        return send_file(log_files[log_type], as_attachment=True)
    
    return jsonify({'error': 'Invalid log type'}), 400

@socketio.on('start_simulation')
def handle_start():
    """Simülasyonu başlat"""
    if not attack_simulator.running:
        attack_simulator.reset()
        log_manager.log('SYSTEM', 'INFO', 
            "User initiated simulation start",
            {'action': 'start_simulation'})
        
        thread = threading.Thread(target=attack_simulator.run_simulation)
        thread.daemon = True
        thread.start()
        
        return {'status': 'started'}
    return {'status': 'already_running'}

@socketio.on('reset_simulation')
def handle_reset():
    """Simülasyonu sıfırla"""
    attack_simulator.reset()
    log_manager.log('SYSTEM', 'INFO', 
        "User initiated simulation reset",
        {'action': 'reset_simulation'})
    
    return {'status': 'reset'}

@socketio.on('connect')
def handle_connect():
    """Client bağlandı"""
    print('Client connected')
    log_manager.log('SYSTEM', 'INFO', 
        "Client connected to WebSocket",
        {'client': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Client ayrıldı"""
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ULTIMATE EVSE P-DoS SIMULATOR")
    print("=" * 80)
    print()
    print("✨ Features:")
    print("  • Real-time terminal output")
    print("  • Complete CAN/OCPP/GPS simulation")
    print("  • Advanced logging system")
    print("  • Beautiful UI with 3D effects")
    print("  • 5-stage attack simulation")
    print()
    print("🌐 Web Interface: http://localhost:5000")
    print("📁 Logs Directory: ./logs/")
    print()
    print("=" * 80)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

