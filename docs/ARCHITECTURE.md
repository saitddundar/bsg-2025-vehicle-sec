# EV-SEC System Architecture

## System Overview

```mermaid
graph TB
    subgraph "EV Charging Ecosystem"
        EV[Electric Vehicle<br/>🚗]
        EVSE[Charging Station<br/>⚡ EVSE]
        CSMS[Central System<br/>🖥️ CSMS]
        Grid[Power Grid<br/>🔌]
    end
    
    subgraph "Attack Surface"
        A1[V2G Manipulation<br/>🎯]
        A2[OCPP Spoofing<br/>🎭]
        A3[Firmware DoS<br/>💣]
        A4[CAN Injection<br/>🔧]
        A5[GPS Spoofing<br/>📍]
    end
    
    subgraph "Security Layer"
        Monitor[Anomaly Detection<br/>🔍]
        Dashboard[Security Dashboard<br/>📊]
        IDS[Future: IDS/IPS<br/>🛡️]
    end
    
    EV <-->|OCPP/ISO15118| EVSE
    EVSE <-->|OCPP 1.6/2.0| CSMS
    EVSE <-->|Energy Flow| Grid
    EV <-->|CAN Bus| EV
    
    A1 -.->|Manipulate| EV
    A2 -.->|Spoof| EVSE
    A3 -.->|Attack| CSMS
    A4 -.->|Inject| EV
    A5 -.->|Fake Location| EV
    
    Monitor -->|Detect| Dashboard
    Monitor -.->|Future| IDS
    
    style EV fill:#ffd600,stroke:#333,stroke-width:2px
    style EVSE fill:#00b4d8,stroke:#333,stroke-width:2px
    style CSMS fill:#4cc9f0,stroke:#333,stroke-width:2px
    style Monitor fill:#06d6a0,stroke:#333,stroke-width:2px
    style Dashboard fill:#118ab2,stroke:#333,stroke-width:2px
    style A1 fill:#ef476f,stroke:#333,stroke-width:2px
    style A2 fill:#ef476f,stroke:#333,stroke-width:2px
    style A3 fill:#ef476f,stroke:#333,stroke-width:2px
    style A4 fill:#ef476f,stroke:#333,stroke-width:2px
    style A5 fill:#ef476f,stroke:#333,stroke-width:2px
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend (React + TypeScript)"
        UI[Dashboard UI<br/>React Components]
        Charts[Recharts<br/>Visualizations]
        WS[WebSocket Client]
    end
    
    subgraph "Backend (Flask + Python)"
        API[REST API<br/>Flask]
        WSS[WebSocket Server<br/>Socket.IO]
        SimEngine[Simulation Engine]
    end
    
    subgraph "Simulations (Python)"
        V2G[V2G Attack]
        SoC[Phantom SoC]
        FW[Firmware PDoS]
        OCPP[OCPP Stealth]
        Others[6 More Scenarios]
    end
    
    UI --> Charts
    UI <-->|HTTP| API
    WS <-->|Real-time Logs| WSS
    API --> SimEngine
    WSS --> SimEngine
    SimEngine --> V2G
    SimEngine --> SoC
    SimEngine --> FW
    SimEngine --> OCPP
    SimEngine --> Others
    
    style UI fill:#118ab2
    style API fill:#06d6a0
    style SimEngine fill:#ffd60a
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant Backend
    participant Simulation
    
    User->>Dashboard: Select Scenario (V2G)
    Dashboard->>Backend: POST /api/simulation/start
    Backend->>Simulation: Start V2G Attack
    
    loop Real-time Updates
        Simulation->>Backend: Generate Anomaly Data
        Backend->>Dashboard: WebSocket: Log Entry
        Dashboard->>User: Update UI & Metrics
    end
    
    User->>Dashboard: Click Stop
    Dashboard->>Backend: POST /api/simulation/stop
    Backend->>Simulation: Terminate
```

## Attack Scenario Categories

<table>
<tr>
<th>Category</th>
<th>Scenarios</th>
<th>Primary Impact</th>
</tr>
<tr>
<td><b>Energy Layer</b></td>
<td>
• V2G Manipulation<br/>
• Phantom SoC Report
</td>
<td>Grid destabilization, billing fraud, battery damage</td>
</tr>
<tr>
<td><b>Network Layer</b></td>
<td>
• OCPP Stealth Beaconing<br/>
• Digital Twin Spoofing
</td>
<td>Data exfiltration, man-in-the-middle, service disruption</td>
</tr>
<tr>
<td><b>Firmware Layer</b></td>
<td>
• Firmware P-DoS Attack
</td>
<td>Permanent hardware damage, costly recovery</td>
</tr>
<tr>
<td><b>Physical Layer</b></td>
<td>
• Siren Attack<br/>
• Ghost ECU Injection<br/>
• Charging While Moving
</td>
<td>Safety hazards, physical damage, bypass safety interlocks</td>
</tr>
<tr>
<td><b>UI Layer</b></td>
<td>
• Display Manipulation
</td>
<td>Phishing, social engineering, payment fraud</td>
</tr>
</table>

## Technology Stack

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS 4, Custom CSS
- **Charts:** Recharts
- **Icons:** Lucide React
- **Animations:** Framer Motion

### Backend
- **Framework:** Flask 3.1
- **WebSocket:** Flask-SocketIO
- **CORS:** Flask-CORS
- **Runtime:** Python 3.10+

### Simulations
- **Protocol:** OCPP 1.6 / 2.0.1
- **Standards:** ISO 15118
- **Networking:** Scapy
- **Analysis:** Python libraries

## Security Detection Logic

### Anomaly Detection Metrics

1. **Energy Flow Inconsistency**
   - Monitor reported vs. actual power transfer
   - Threshold: ±10% deviation triggers warning

2. **Network Anomalies**
   - Latency: Normal <50ms, Anomaly >100ms
   - Packet Loss: Normal <0.1%, Anomaly >1%
   - Payload Size: Detect oversized heartbeats

3. **GPS/Location Verification**
   - Cross-check GPS with geofence
   - Motion detection during charging
   - Threshold: >5m deviation = alert

4. **CAN Bus Monitoring**
   - Detect unauthorized ECU responses
   - Frame replay detection via timestamps
   - Arbitration ID whitelist validation

5. **Firmware Integrity**
   - Hash verification
   - Boot sector validation
   - Rollback protection

## Future Enhancements

- [ ] Machine Learning-based anomaly scoring
- [ ] Integration with Snort/Suricata IDS
- [ ] Honeypot deployment for threat intelligence
- [ ] Real EVSE hardware integration
- [ ] Blockchain-based audit trail
- [ ] Advanced visualization (3D network topology)
