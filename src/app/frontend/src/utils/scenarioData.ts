// Scenario-specific data generators and anomaly logic

export interface ScenarioConfig {
    id: string;
    name: string;
    author: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    status: 'normal' | 'suspicious' | 'attack';
    description: string;
    anomalyType: 'energy' | 'network' | 'firmware' | 'gps' | 'can' | 'display';
    attackVector: string;
}

export interface AnomalyData {
    energyFlowAnomaly: number; // percentage of anomaly in energy flow
    networkLatency: number; // ms
    packetLoss: number; // percentage
    socAnomaly: boolean;
    gpsDeviation: number; // meters
    canBusError: boolean;
    firmwareHash: 'valid' | 'pending' | 'invalid';
    // EV & Charging metrics
    stateOfCharge: number; // percentage
    vppPowerFlow: number; // kW
    chargingRate: number; // kW
    activeThreats: number;
}

export const scenarioConfigs: ScenarioConfig[] = [
    {
        id: 'v2g-mod',
        name: 'V2G Protocol Manipulation',
        author: 'Sait Dundar',
        severity: 'critical',
        status: 'attack',
        description: 'Manipulating V2G protocol to destabilize microgrid',
        anomalyType: 'energy',
        attackVector: 'ISO 15118 / OCPP Manipulation'
    },
    {
        id: 'phantom-soc',
        name: 'Phantom SoC Report',
        author: 'Kardelen Demir',
        severity: 'high',
        status: 'suspicious',
        description: 'Forging State of Charge telemetry data',
        anomalyType: 'energy',
        attackVector: 'MeterValues Fraud'
    },
    {
        id: 'firmware-pdos',
        name: 'Firmware P-DoS Attack',
        author: 'Betül Altunyuva',
        severity: 'critical',
        status: 'normal',
        description: 'Permanent Denial of Service via firmware corruption',
        anomalyType: 'firmware',
        attackVector: 'Firmware Update Abuse'
    },
    {
        id: 'ocpp-stealth',
        name: 'OCPP Stealth Beaconing',
        author: 'Göksu Kayar',
        severity: 'high',
        status: 'normal',
        description: 'Covert C2 channel via heartbeat messages',
        anomalyType: 'network',
        attackVector: 'Message Payload Injection'
    },
    {
        id: 'digital-twin',
        name: 'Digital Twin Spoofing',
        author: 'Mehmet Erdem Abacı',
        severity: 'medium',
        status: 'normal',
        description: 'Impersonating charging station identity',
        anomalyType: 'network',
        attackVector: 'Identity Spoofing'
    },
    {
        id: 'siren-attack',
        name: 'Siren Attack',
        author: 'BSG Team',
        severity: 'critical',
        status: 'normal',
        description: 'Physical attack via CAN bus manipulation',
        anomalyType: 'can',
        attackVector: 'CAN Frame Injection'
    },
    {
        id: 'disp-manip',
        name: 'Display Manipulation',
        author: 'BSG Team',
        severity: 'medium',
        status: 'normal',
        description: 'Malicious UI content injection',
        anomalyType: 'display',
        attackVector: 'DataTransfer Payload'
    },
    {
        id: 'charge-move',
        name: 'Charging While Moving',
        author: 'BSG Team',
        severity: 'high',
        status: 'normal',
        description: 'GPS-lock bypass causing safety hazard',
        anomalyType: 'gps',
        attackVector: 'Sensor Spoofing'
    },
    {
        id: 'ghost-ecu',
        name: 'Ghost ECU Injection',
        author: 'BSG Team',
        severity: 'critical',
        status: 'normal',
        description: 'Replay attack mimicking legitimate ECU',
        anomalyType: 'can',
        attackVector: 'CAN Replay'
    }
];

// Generate scenario-specific anomaly data
export function generateAnomalyData(scenarioId: string, isRunning: boolean): AnomalyData {
    const config = scenarioConfigs.find(s => s.id === scenarioId);

    // Base normal values
    const baseData: AnomalyData = {
        energyFlowAnomaly: 0,
        networkLatency: 42,
        packetLoss: 0.02,
        socAnomaly: false,
        gpsDeviation: 0,
        canBusError: false,
        firmwareHash: 'valid',
        stateOfCharge: 67,
        vppPowerFlow: 2.4,
        chargingRate: 7.2,
        activeThreats: 0
    };

    if (!config || !isRunning) {
        return baseData;
    }

    // Calculate threats based on scenario status
    let threats = 0;
    if (config.status === 'attack') threats = 1;
    else if (config.status === 'suspicious') threats = 0;

    switch (config.anomalyType) {
        case 'energy':
            return {
                ...baseData,
                energyFlowAnomaly: config.status === 'attack' ? 35 + Math.random() * 15 : 5 + Math.random() * 10,
                socAnomaly: config.id === 'phantom-soc',
                networkLatency: 45 + Math.random() * 10,
                stateOfCharge: config.id === 'phantom-soc' ? 82 + Math.random() * 10 : 67 - Math.random() * 10,
                vppPowerFlow: config.id === 'v2g-mod' ? -5.2 + Math.random() * 3 : 2.4 + Math.random() * 1,
                chargingRate: config.id === 'v2g-mod' ? 12.5 + Math.random() * 5 : 7.2 + Math.random() * 2,
                activeThreats: threats
            };

        case 'network':
            return {
                ...baseData,
                networkLatency: 120 + Math.random() * 80,
                packetLoss: 2.5 + Math.random() * 3,
                energyFlowAnomaly: 5 + Math.random() * 5,
                chargingRate: 6.8 + Math.random() * 1.5,
                activeThreats: threats
            };

        case 'firmware':
            return {
                ...baseData,
                firmwareHash: 'invalid',
                energyFlowAnomaly: 10 + Math.random() * 15,
                networkLatency: 200 + Math.random() * 100,
                chargingRate: 3.2 + Math.random() * 2,
                stateOfCharge: 65 - Math.random() * 5,
                activeThreats: threats
            };

        case 'gps':
            return {
                ...baseData,
                gpsDeviation: 50 + Math.random() * 100,
                energyFlowAnomaly: 25 + Math.random() * 20,
                chargingRate: config.id === 'charge-move' ? 0 : 7.2,
                stateOfCharge: config.id === 'charge-move' ? 45 + Math.random() * 10 : 67,
                activeThreats: threats
            };

        case 'can':
            return {
                ...baseData,
                canBusError: true,
                networkLatency: 85 + Math.random() * 40,
                energyFlowAnomaly: 15 + Math.random() * 25,
                chargingRate: 6.5 + Math.random() * 2,
                activeThreats: threats
            };

        case 'display':
            return {
                ...baseData,
                networkLatency: 55 + Math.random() * 20,
                energyFlowAnomaly: 8 + Math.random() * 10,
                chargingRate: 7.0 + Math.random() * 1,
                activeThreats: threats
            };
    }

    return baseData;
}

// Generate scenario-specific log messages
export function generateScenarioLog(scenarioId: string): string {
    const config = scenarioConfigs.find(s => s.id === scenarioId);
    if (!config) return "System nominal";

    const logMessages: Record<string, string[]> = {
        'v2g-mod': [
            "V2G energy transfer anomaly detected [⚠️ -15kW deviation]",
            "ISO 15118 protocol violation: unexpected power flow direction",
            "Microgrid frequency deviation: 50.8Hz (threshold exceeded)",
            "V2G session authentication challenge failed",
            "Energy meter discrepancy: reported vs actual +22%"
        ],
        'phantom-soc': [
            "SoC telemetry mismatch detected [reported: 87%, actual: 62%]",
            "MeterValues inconsistency: charging curve anomaly",
            "Battery management system checksum error",
            "SoC jump detected: +15% in 30 seconds (impossible)",
            "Cross-sensor validation failed: voltage/SoC mismatch"
        ],
        'firmware-pdos': [
            "Firmware update request from unauthorized source",
            "Firmware hash verification FAILED [critical]",
            "Boot sector corruption detected",
            "Firmware rollback protection triggered",
            "Emergency recovery mode activated"
        ],
        'ocpp-stealth': [
            "Heartbeat payload size anomaly: +120 bytes",
            "Unusual heartbeat frequency pattern detected",
            "Encrypted payload in heartbeat message [suspicious]",
            "C2 beacon signature detected in OCPP traffic",
            "IDS alert: stealth channel in protocol messages"
        ],
        'digital-twin': [
            "Station identity verification failed",
            "Duplicate charge point ID detected on network",
            "TLS certificate mismatch for station endpoint",
            "Charging station impersonation attempt blocked",
            "Identity spoofing detected: IP/MAC mismatch"
        ],
        'siren-attack': [
            "CAN bus frame injection detected [ID: 0x3F2]",
            "Emergency siren activated without valid trigger",
            "CAN arbitration anomaly: unauthorized ECU",
            "Physical safety interlock bypassed",
            "Horn/siren control signal spoofed"
        ],
        'disp-manip': [
            "DataTransfer payload contains suspicious HTML",
            "Display injection attempt: phishing content detected",
            "UI rendering anomaly: unauthorized payment prompt",
            "XSS pattern detected in display message",
            "Malicious QR code payload intercepted"
        ],
        'charge-move': [
            "GPS lock lost during active charging session",
            "Vehicle motion detected while charging [CRITICAL]",
            "Geofence violation: 150m from station location",
            "Accelerometer data inconsistent with GPS lock",
            "Safety interlock override attempt detected"
        ],
        'ghost-ecu': [
            "Duplicate ECU detected on CAN bus",
            "CAN frame replay attack identified [ID: 0x241]",
            "Unauthorized ECU responding to diagnostic requests",
            "Timestamp anomaly in CAN frames (replay signature)",
            "Ghost ECU injection: spoofed valid ECU messages"
        ]
    };

    const messages = logMessages[scenarioId] || ["System event logged"];
    return messages[Math.floor(Math.random() * messages.length)];
}

// Generate scenario-specific time series data
export function generateScenarioTimeSeries(scenarioId: string, isRunning: boolean) {
    const config = scenarioConfigs.find(s => s.id === scenarioId);
    const points = 24;

    return Array.from({ length: points }, (_, i) => {
        const baseValue = 100 + Math.random() * 50;
        let anomalousValue = 0;
        let socValue = 80 - i * 0.5 + (Math.random() - 0.5) * 2;

        if (isRunning && config) {
            switch (config.anomalyType) {
                case 'energy':
                    // Energy attacks show spikes in consumption/transfer
                    anomalousValue = i > 10 && Math.random() > 0.3 ? Math.random() * 40 + 20 : 0;
                    if (config.id === 'phantom-soc') {
                        socValue += Math.random() * 15; // Abnormal SoC increases
                    }
                    break;
                case 'network':
                    // Network attacks show packet anomalies
                    anomalousValue = Math.random() > 0.4 ? Math.random() * 25 : 0;
                    break;
                case 'firmware':
                    // Firmware attacks cause system instability
                    anomalousValue = i > 15 ? Math.random() * 50 : 0;
                    break;
                case 'gps':
                case 'can':
                    // Physical attacks show erratic patterns
                    anomalousValue = Math.random() > 0.5 ? Math.random() * 30 : 0;
                    break;
            }
        }

        return {
            time: `${i}:00`,
            value: baseValue,
            anomalous: anomalousValue,
            soc: Math.max(20, Math.min(100, socValue))
        };
    });
}
