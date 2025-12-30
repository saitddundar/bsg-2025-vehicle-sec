import { useState, useEffect } from 'react';
import {
    VehicleInfo,
    LogViewer,
    NetworkTopology,
    AnomalyScore,
    MetricsChart,
    PacketInspector,
    SimulationSelector,
} from '../../components';
import type { Simulation } from '../../types';
import './Dashboard.css';

// Mock data
const mockSimulations: Simulation[] = [
    {
        id: 'sait-simulation',
        name: 'V2G Protocol Manipulation',
        description: 'Attacks on Vehicle-to-Grid protocol and microgrid destabilization',
        path: 'simulations/sait-simulation',
        author: 'Sait Dundar',
        status: 'idle',
        scripts: [
            { name: 'CSMS Server', file: 'csms_server.py', description: 'Central System' },
            { name: 'V2G Attacker', file: 'v2g_attacker.py', description: 'Attack Simulator' },
        ],
    },
    {
        id: 'erdem-simulasyon',
        name: 'OCPP & CAN-Bus',
        description: 'Protocol analysis and CAN-Bus anomaly detection',
        path: 'simulations/erdem-simulasyon',
        author: 'Erdem',
        status: 'idle',
        scripts: [
            { name: 'Data Collector', file: 'data_collector.py', description: 'Anomaly Detection' },
        ],
    },
    {
        id: 'sevval-simulasyon',
        name: 'MITM Attack',
        description: 'Man-in-the-Middle attack on charging infrastructure',
        path: 'simulations/sevval-simulasyon',
        author: 'Sevval',
        status: 'idle',
        scripts: [
            { name: 'MITM', file: 'mitm.py', description: 'Attack' },
        ],
    },
];

type ThreatLevel = 'low' | 'medium' | 'high' | 'critical';

export function Dashboard() {
    const [simulations, setSimulations] = useState<Simulation[]>(mockSimulations);
    const [logs, setLogs] = useState<string[]>([]);
    const [activeSimulation, setActiveSimulation] = useState<string | null>(null);
    const [threatLevel, setThreatLevel] = useState<ThreatLevel>('low');
    const [anomalyCount, setAnomalyCount] = useState(0);
    const [attackerPresent, setAttackerPresent] = useState(false);
    const [aiScore, setAiScore] = useState(12);
    const [elapsedTime, setElapsedTime] = useState(0);

    // Simulation effects
    useEffect(() => {
        if (!activeSimulation) return;

        const logInterval = setInterval(() => {
            const messages = [
                '[INFO] Processing data stream...',
                '[INFO] Monitoring network traffic...',
                '[INFO] Analyzing packet signatures...',
                '[INFO] Checking protocol integrity...',
            ];
            setLogs((prev) => [
                ...prev,
                `[${new Date().toLocaleTimeString()}] ${messages[Math.floor(Math.random() * messages.length)]}`,
            ]);
        }, 2000);

        const threatInterval = setInterval(() => {
            setElapsedTime((prev) => prev + 1);
        }, 1000);

        return () => {
            clearInterval(logInterval);
            clearInterval(threatInterval);
        };
    }, [activeSimulation]);

    // Attack progression
    useEffect(() => {
        if (!activeSimulation) return;

        if (elapsedTime > 5 && elapsedTime < 15) {
            setThreatLevel('medium');
            if (elapsedTime === 6) {
                setAnomalyCount((prev) => prev + 1);
                setLogs((prev) => [
                    ...prev,
                    `[${new Date().toLocaleTimeString()}] [WARNING] Unusual pattern detected`,
                ]);
            }
            setAiScore(45);
        } else if (elapsedTime >= 15 && elapsedTime < 25) {
            setThreatLevel('high');
            setAttackerPresent(true);
            if (elapsedTime === 15) {
                setAnomalyCount((prev) => prev + 2);
                setLogs((prev) => [
                    ...prev,
                    `[${new Date().toLocaleTimeString()}] [ALERT] Possible intrusion detected`,
                ]);
            }
            setAiScore(78);
        } else if (elapsedTime >= 25) {
            setThreatLevel('critical');
            setAiScore(92);
            if (elapsedTime === 25) {
                setLogs((prev) => [
                    ...prev,
                    `[${new Date().toLocaleTimeString()}] [CRITICAL] Active attack confirmed!`,
                ]);
            }
        }
    }, [elapsedTime, activeSimulation]);

    const handleSelectSimulation = (simulation: Simulation) => {
        setSimulations((prev) =>
            prev.map((s) =>
                s.id === simulation.id
                    ? { ...s, status: 'running' as const }
                    : { ...s, status: 'idle' as const }
            )
        );
        setActiveSimulation(simulation.id);
        setThreatLevel('low');
        setAnomalyCount(0);
        setAttackerPresent(false);
        setAiScore(12);
        setElapsedTime(0);

        setLogs([
            `[${new Date().toLocaleTimeString()}] [INIT] Starting ${simulation.name}...`,
            `[${new Date().toLocaleTimeString()}] [OK] Systems initialized`,
            `[${new Date().toLocaleTimeString()}] [INFO] Monitoring active...`,
        ]);
    };

    const handleStopSimulation = () => {
        const sim = simulations.find(s => s.id === activeSimulation);
        if (sim) {
            setSimulations((prev) =>
                prev.map((s) =>
                    s.id === sim.id ? { ...s, status: 'completed' as const } : s
                )
            );
        }
        setActiveSimulation(null);
        setThreatLevel('low');
        setAttackerPresent(false);

        setLogs((prev) => [
            ...prev,
            `[${new Date().toLocaleTimeString()}] [STOP] Simulation terminated`,
            `[${new Date().toLocaleTimeString()}] [SUMMARY] Anomalies: ${anomalyCount}`,
        ]);
    };

    const getConnectionStatus = () => {
        if (threatLevel === 'critical') return 'intercepted' as const;
        if (threatLevel === 'high') return 'compromised' as const;
        return 'secure' as const;
    };

    const getNodeStatus = (node: string) => {
        if (!activeSimulation) return 'offline' as const;
        if (threatLevel === 'critical') return 'attack' as const;
        if (threatLevel === 'high' && node === 'evse') return 'warning' as const;
        return 'normal' as const;
    };

    return (
        <div className="dashboard">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <span className="brand-logo">BSG 2025</span>
                </div>
                <div className="header-center">
                    <span className="header-subtitle">Vehicle Security Platform</span>
                </div>
                <div className="header-right">
                    <SimulationSelector
                        simulations={simulations}
                        activeSimulation={activeSimulation}
                        onSelect={handleSelectSimulation}
                        onStop={handleStopSimulation}
                    />
                </div>
            </header>

            {/* Main 3-Column Layout */}
            <main className="dashboard-main">
                {/* Left Column - Vehicle Status */}
                <div className="column column-left">
                    <VehicleInfo vehicle={null} isConnected={activeSimulation !== null} />
                    <AnomalyScore
                        score={aiScore}
                        attackType="V2G Injection"
                        confidence={aiScore > 70 ? 'high' : aiScore > 40 ? 'medium' : 'low'}
                        lastUpdate={new Date().toLocaleTimeString()}
                    />
                </div>

                {/* Center Column - Topology & Charts */}
                <div className="column column-center">
                    <NetworkTopology
                        vehicleStatus={getNodeStatus('vehicle')}
                        evseStatus={getNodeStatus('evse')}
                        csmsStatus={getNodeStatus('csms')}
                        connectionStatus={getConnectionStatus()}
                        attackerPresent={attackerPresent}
                        attackType={attackerPresent ? 'MITM' : undefined}
                    />
                    <MetricsChart
                        isRunning={activeSimulation !== null}
                        hasAnomaly={threatLevel !== 'low'}
                        anomalyIndex={12}
                    />
                </div>

                {/* Right Column - Console & Packets */}
                <div className="column column-right">
                    <LogViewer
                        logs={logs}
                        isRunning={activeSimulation !== null}
                    />
                    <PacketInspector
                        packets={[]}
                        isRunning={activeSimulation !== null}
                    />
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
