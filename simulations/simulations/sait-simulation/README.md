# V2G Protocol Manipulation Simulation

## Scenario Description

This simulation demonstrates the **V2G (Vehicle-to-Grid) Protocol Manipulation** attack and how this attack can lead to **Microgrid Destabilization**.

### Attack Vector

1. **ISO 15118 / OCPP Protocol Manipulation**: The attacker intercepts the communication between the EV and the charging station to inject fake V2G commands.
2. **Fake Energy Transfer Data**: The amount of energy the vehicle sends to the grid is manipulated.
3. **Coordinated Attack**: Multiple EVs are manipulated simultaneously to create sudden voltage/frequency fluctuations in the grid.

### Simulation Components

| File | Description |
|------|-------------|
| `csms_server.py` | OCPP 1.6 CSMS (Central System Management Server) |
| `charging_station.py` | Charging Station (EVSE) Simulator |
| `ev_simulator.py` | Electric Vehicle (EV) and V2G Simulator |
| `microgrid_monitor.py` | Microgrid Monitoring and Anomaly Detection System |
| `v2g_attacker.py` | V2G Protocol Manipulation Attack Simulator |

### Running the Simulation

```bash
# 1. Create a virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the CSMS server (Terminal 1)
python csms_server.py

# 4. Start the charging station (Terminal 2)
python charging_station.py

# 5. Normal EV simulation (Terminal 3)
python ev_simulator.py --mode normal

# 6. Start the microgrid monitor (Terminal 4)
python microgrid_monitor.py

# 7. Start the attack simulation (Terminal 5)
python v2g_attacker.py --attack-type injection
```

### Attack Modes

- `normal`: Normal V2G operation (charge/discharge)
- `injection`: Fake energy data injection
- `flooding`: DoS attack by sending excessive V2G commands
- `destabilize`: Grid destabilization via coordinated attack

### Anomaly Detection Logic

1. **Energy Flow Inconsistency**: Requested vs. actual energy transfer
2. **Frequency Deviation**: Normally 50Hz, tolerance +/-0.5Hz
3. **Voltage Fluctuation**: Normally 230V, tolerance +/-10V
4. **Sudden Load Change**: Unexpected increase in power demand

## License

BSG 2025 Vehicle Security Project
