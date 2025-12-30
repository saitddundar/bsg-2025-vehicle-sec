import { useState, useEffect } from 'react';
import {
    Header,
    VehicleInfo,
    LogViewer,
    NetworkTopology,
    AnomalyScore,
    MetricsChart,
    PacketInspector,
    ThreatSummary,
    AttackTimeline,
} from '../../components';
import { Play, Square } from 'lucide-react';
import type { Simulation } from '../../types';
import './Dashboard.css';

const SCOPE_SIMULATIONS: Simulation[] = [
    {
        id: 'v2g-injection',
        name: 'V2G Manipulation',
        description: 'Intercepting V2G handshake to manipulate grid discharge',
        path: '', author: 'BSG', status: 'idle', scripts: []
    },
    {
        id: 'ocpp-replay',
        name: 'OCPP Replay',
        description: 'Replaying authorization packets to start fraudulent session',
        path: '', author: 'BSG', status: 'idle', scripts: []
    },
    {
        id: 'can-flood',
        name: 'CAN Bus DoS',
        description: 'Flooding vehicle bus to disable safety systems during charging',
        path: '', author: 'BSG', status: 'idle', scripts: []
    },
    {
        id: 'firmware-tampering',
        name: 'Firmware Spoof',
        description: 'Injecting malicious firmware metadata into CSMS handshake',
        path: '', author: 'BSG', status: 'idle', scripts: []
    }
];

export function Dashboard() {
    const [activeSim, setActiveSim] = useState<Simulation | null>(null);
    const [elapsed, setElapsed] = useState(0);
    const [anomalyState, setAnomalyState] = useState<'normal' | 'suspicious' | 'attack'>('normal');

    useEffect(() => {
        let timer: any;
        if (activeSim) {
            timer = setInterval(() => setElapsed(e => e + 1), 1000);
        } else {
            setElapsed(0);
            setAnomalyState('normal');
        }
        return () => clearInterval(timer);
    }, [activeSim]);

    useEffect(() => {
        if (elapsed > 10 && elapsed <= 20) setAnomalyState('suspicious');
        else if (elapsed > 20) setAnomalyState('attack');
        else setAnomalyState('normal');
    }, [elapsed]);

    const handleToggleSim = (sim: Simulation) => {
        if (activeSim?.id === sim.id) {
            setActiveSim(null);
        } else {
            setActiveSim(sim);
        }
    };

    return (
        <div className={`dashboard-root state-${anomalyState}`}>
            <Header activeSimulation={activeSim?.name} anomalyState={anomalyState} />

            <main className="dashboard-content">
                {/* Left Column: Attack Scenarios (Top) & Kill Chain (Bottom) */}
                <aside className="column-left">
                    <div className="section-half scenarios">
                        <span className="section-label">Attack Scenarios</span>
                        <div className="scenario-list">
                            {SCOPE_SIMULATIONS.map(sim => (
                                <button
                                    key={sim.id}
                                    className={`scenario-card ${activeSim?.id === sim.id ? 'active' : ''}`}
                                    onClick={() => handleToggleSim(sim)}
                                >
                                    <div className="scenario-info">
                                        <span className="scenario-name">{sim.name}</span>
                                        <span className="scenario-desc">{sim.description}</span>
                                    </div>
                                    {activeSim?.id === sim.id ? <Square size={14} fill="currentColor" /> : <Play size={14} />}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="section-half kill-chain">
                        <AttackTimeline
                            recon={elapsed > 5}
                            injection={elapsed > 15}
                            detection={elapsed > 25}
                        />
                    </div>
                </aside>

                {/* Center Column: Network Arch & Live Parameters (50/50 Height) */}
                <section className="column-center">
                    <div className="center-half topology">
                        <NetworkTopology
                            vehicleStatus={anomalyState === 'attack' ? 'attack' : 'normal'}
                            evseStatus={anomalyState === 'suspicious' ? 'warning' : 'normal'}
                            csmsStatus="normal"
                            connectionStatus={anomalyState === 'normal' ? 'secure' : 'compromised'}
                            attackerPresent={anomalyState !== 'normal'}
                            flowDirection={activeSim ? (anomalyState === 'attack' ? 'discharging' : 'charging') : 'idle'}
                        />
                    </div>
                    <div className="center-half metrics">
                        <MetricsChart isRunning={!!activeSim} anomalyState={anomalyState} />
                    </div>
                </section>

                {/* Right Column: Console -> Diagnosis -> Asset */}
                <aside className="column-right">
                    <div className="right-section console">
                        <LogViewer isRunning={!!activeSim} logs={[]} />
                    </div>
                    <div className="right-section diagnosis">
                        <AnomalyScore score={activeSim ? (anomalyState === 'attack' ? 92 : anomalyState === 'suspicious' ? 45 : 12) : 0} />
                    </div>
                    <div className="right-section asset">
                        <VehicleInfo vehicle={null} isConnected={!!activeSim} />
                    </div>
                </aside>
            </main>
        </div>
    );
}

export default Dashboard;
