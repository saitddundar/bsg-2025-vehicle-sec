import { useState } from 'react';
import { Header, SimulationCard, LogViewer } from '../../components';
import type { Simulation } from '../../types';
import './Dashboard.css';

// Mock data - will be replaced with API calls
const mockSimulations: Simulation[] = [
    {
        id: 'sait-simulation',
        name: 'V2G Protocol Manipulation',
        description: 'Simulates V2G protocol manipulation attacks on microgrid systems. Includes CSMS server, charging station, and attacker modules.',
        path: 'simulations/sait-simulation',
        author: 'Sait Dundar',
        status: 'idle',
        scripts: [
            { name: 'CSMS Server', file: 'csms_server.py', description: 'Central System Management Server' },
            { name: 'Charging Station', file: 'charging_station.py', description: 'EV Charging Station Simulator' },
            { name: 'V2G Attacker', file: 'v2g_attacker.py', description: 'V2G Protocol Attack Simulator' },
            { name: 'Full Simulation', file: 'v2g_simulation.py', description: 'Combined V2G Simulation' },
            { name: 'Microgrid Monitor', file: 'microgrid_monitor.py', description: 'Microgrid Monitoring System' },
        ],
    },
    {
        id: 'erdem-simulasyon',
        name: 'OCPP & CAN-Bus Simulation',
        description: 'Simulates OCPP charging communication and CAN-Bus vehicle data with anomaly detection capabilities.',
        path: 'simulations/erdem-simulasyon',
        author: 'Erdem',
        status: 'idle',
        scripts: [
            { name: 'CSMS Server', file: 'csms_sunucu.py', description: 'OCPP Central Server' },
            { name: 'Charging Station', file: 'istasyon.py', description: 'Charging Station' },
            { name: 'CAN Simulator', file: 'can_simulator.py', description: 'CAN-Bus Data Simulator' },
            { name: 'GPS Simulator', file: 'gps_simulator.py', description: 'GPS/Telematics Simulator' },
            { name: 'Data Collector', file: 'data_collector.py', description: 'Data Collection & Anomaly Detection' },
        ],
    },
    {
        id: 'sevval-simulasyon',
        name: 'MITM Attack Simulation',
        description: 'Man-in-the-Middle attack simulation on EV charging infrastructure.',
        path: 'simulations/sevval-simulasyon',
        author: 'Sevval',
        status: 'idle',
        scripts: [
            { name: 'CSMS', file: 'csms.py', description: 'Central System' },
            { name: 'EV', file: 'ev.py', description: 'Electric Vehicle Simulator' },
            { name: 'MITM', file: 'mitm.py', description: 'Man-in-the-Middle Attack' },
        ],
    },
];

export function Dashboard() {
    const [simulations, setSimulations] = useState<Simulation[]>(mockSimulations);
    const [logs, setLogs] = useState<string[]>([]);
    const [activeSimulation, setActiveSimulation] = useState<string | null>(null);

    const handleRunSimulation = (simulation: Simulation) => {
        // Update status
        setSimulations((prev) =>
            prev.map((s) =>
                s.id === simulation.id ? { ...s, status: 'running' as const } : s
            )
        );
        setActiveSimulation(simulation.id);

        // Mock log output
        setLogs([
            `[${new Date().toLocaleTimeString()}] Starting ${simulation.name}...`,
            `[${new Date().toLocaleTimeString()}] Loading scripts from ${simulation.path}`,
            `[${new Date().toLocaleTimeString()}] [OK] Simulation initialized`,
        ]);

        // Simulate running logs
        const interval = setInterval(() => {
            setLogs((prev) => [
                ...prev,
                `[${new Date().toLocaleTimeString()}] [INFO] Simulation running... Step ${prev.length - 2}`,
            ]);
        }, 2000);

        // Store interval ID for cleanup
        (window as any).simulationInterval = interval;
    };

    const handleStopSimulation = (simulation: Simulation) => {
        // Clear interval
        if ((window as any).simulationInterval) {
            clearInterval((window as any).simulationInterval);
        }

        // Update status
        setSimulations((prev) =>
            prev.map((s) =>
                s.id === simulation.id ? { ...s, status: 'completed' as const } : s
            )
        );
        setActiveSimulation(null);

        setLogs((prev) => [
            ...prev,
            `[${new Date().toLocaleTimeString()}] [OK] Simulation stopped`,
            `[${new Date().toLocaleTimeString()}] Cleaning up...`,
            `[${new Date().toLocaleTimeString()}] Done.`,
        ]);
    };

    return (
        <div className="dashboard">
            <Header />

            <main className="dashboard-main">
                <div className="dashboard-content">
                    <section className="simulations-section">
                        <div className="section-header">
                            <h2>Available Simulations</h2>
                            <span className="simulation-count">{simulations.length} simulations</span>
                        </div>

                        <div className="simulations-grid">
                            {simulations.map((simulation) => (
                                <SimulationCard
                                    key={simulation.id}
                                    simulation={simulation}
                                    onRun={handleRunSimulation}
                                    onStop={handleStopSimulation}
                                />
                            ))}
                        </div>
                    </section>

                    <section className="logs-section">
                        <LogViewer
                            logs={logs}
                            isRunning={activeSimulation !== null}
                        />
                    </section>
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
