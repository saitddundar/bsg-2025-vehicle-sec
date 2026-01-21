from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Simülasyon durumu
simulation_state = {
    'running': False,
    'scenario_id': None,
    'start_time': None,
    'logs': []
}

# Scenario configurations
SCENARIOS = {
    'v2g-mod': {
        'name': 'V2G Protocol Manipulation',
        'logs': [
            "V2G energy transfer anomaly detected [⚠️ -15kW deviation]",
            "ISO 15118 protocol violation: unexpected power flow direction",
            "Microgrid frequency deviation: 50.8Hz (threshold exceeded)",
            "V2G session authentication challenge failed",
            "Energy meter discrepancy: reported vs actual +22%"
        ]
    },
    'phantom-soc': {
        'name': 'Phantom SoC Report',
        'logs': [
            "SoC telemetry mismatch detected [reported: 87%, actual: 62%]",
            "MeterValues inconsistency: charging curve anomaly",
            "Battery management system checksum error",
            "SoC jump detected: +15% in 30 seconds (impossible)",
            "Cross-sensor validation failed: voltage/SoC mismatch"
        ]
    },
    'firmware-pdos': {
        'name': 'Firmware P-DoS Attack',
        'logs': [
            "Firmware update request from unauthorized source",
            "Firmware hash verification FAILED [critical]",
            "Boot sector corruption detected",
            "Firmware rollback protection triggered",
            "Emergency recovery mode activated"
        ]
    },
    'ocpp-stealth': {
        'name': 'OCPP Stealth Beaconing',
        'logs': [
            "Heartbeat payload size anomaly: +120 bytes",
            "Unusual heartbeat frequency pattern detected",
            "Encrypted payload in heartbeat message [suspicious]",
            "C2 beacon signature detected in OCPP traffic",
            "IDS alert: stealth channel in protocol messages"
        ]
    },
    'digital-twin': {
        'name': 'Digital Twin Spoofing',
        'logs': [
            "Station identity verification failed",
            "Duplicate charge point ID detected on network",
            "TLS certificate mismatch for station endpoint",
            "Charging station impersonation attempt blocked",
            "Identity spoofing detected: IP/MAC mismatch"
        ]
    }
}

def log_generator():
    """Background thread for generating logs during simulation"""
    while True:
        if simulation_state['running'] and simulation_state['scenario_id']:
            scenario_id = simulation_state['scenario_id']
            if scenario_id in SCENARIOS:
                logs = SCENARIOS[scenario_id]['logs']
                message = random.choice(logs)
                
                is_anomaly = '⚠️' in message or 'FAIL' in message or 'anomaly' in message.lower()
                log_entry = {
                    'id': str(random.randint(1000000, 9999999)),
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'error' if is_anomaly else ('warn' if random.random() > 0.7 else 'info'),
                    'message': message
                }
                
                simulation_state['logs'].insert(0, log_entry)
                simulation_state['logs'] = simulation_state['logs'][:50]  # Keep last 50 logs
                
                # Emit to all connected clients
                socketio.emit('log_update', log_entry, namespace='/')
        
        time.sleep(random.uniform(1.5, 3.5))

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify([
        {'id': sid, 'name': SCENARIOS[sid]['name']} 
        for sid in SCENARIOS.keys()
    ])

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    data = request.json
    scenario_id = data.get('scenario_id')
    
    if scenario_id not in SCENARIOS:
        return jsonify({'error': 'Invalid scenario'}), 400
    
    simulation_state['running'] = True
    simulation_state['scenario_id'] = scenario_id
    simulation_state['start_time'] = datetime.now()
    simulation_state['logs'] = []
    
    return jsonify({
        'status': 'started',
        'scenario_id': scenario_id,
        'scenario_name': SCENARIOS[scenario_id]['name']
    })

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    simulation_state['running'] = False
    return jsonify({'status': 'stopped'})

@app.route('/api/simulation/status', methods=['GET'])
def get_status():
    return jsonify({
        'running': simulation_state['running'],
        'scenario_id': simulation_state['scenario_id'],
        'start_time': simulation_state['start_time'].isoformat() if simulation_state['start_time'] else None,
        'uptime': (datetime.now() - simulation_state['start_time']).seconds if simulation_state['start_time'] else 0
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(simulation_state['logs'])

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'ok'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Start log generator thread
    log_thread = threading.Thread(target=log_generator, daemon=True)
    log_thread.start()
    
    print("🚀 EV Security Backend API Starting...")
    print("📡 Server: http://localhost:5000")
    print("🔌 WebSocket: ws://localhost:5000/socket.io")
    print("\nEndpoints:")
    print("  GET  /api/health")
    print("  GET  /api/scenarios")
    print("  POST /api/simulation/start")
    print("  POST /api/simulation/stop")
    print("  GET  /api/simulation/status")
    print("  GET  /api/logs")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
