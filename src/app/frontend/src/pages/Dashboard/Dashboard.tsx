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
import { Play, Square, Settings, Database, Activity, LayoutGrid } from 'lucide-react';
import type { Simulation } from '../../types';
import './Dashboard.css';

const SCOPE_SIMULATIONS: Simulation[] = [
    {
        id: 'sait-simulation',
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
                {/* Left Column: Navigation & Scenarios */}
                <aside className="nav-column">
                    <div className="section-group">
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

                    <div className="section-group">
                        <span className="section-label">Resources</span>
                        <nav className="side-nav">
                            <button className="nav-item active"><LayoutGrid size={16} /> Overview</button>
                            <button className="nav-item"><Database size={16} /> Protocol Library</button>
                            <button className="nav-item"><Settings size={16} /> Device Management</button>
                            <button className="nav-item"><Activity size={16} /> Global Stats</button>
                        </nav>
                    </div>

                    <div className="section-group spacer">
                        <AttackTimeline
                            recon={elapsed > 5}
                            injection={elapsed > 15}
                            detection={elapsed > 25}
                        />
                    </div>
                </aside>

                {/* Center Column: Core Analysis */}
                <section className="main-column">
                    <div className="topology-box">
                        <NetworkTopology
                            vehicleStatus={anomalyState === 'attack' ? 'attack' : 'normal'}
                            evseStatus={anomalyState === 'suspicious' ? 'warning' : 'normal'}
                            csmsStatus="normal"
                            connectionStatus={anomalyState === 'normal' ? 'secure' : 'compromised'}
                            attackerPresent={anomalyState !== 'normal'}
                            flowDirection={activeSim ? (anomalyState === 'attack' ? 'discharging' : 'charging') : 'idle'}
                        />
                    </div>
                    <div className="metrics-box">
                        <MetricsChart isRunning={!!activeSim} anomalyState={anomalyState} />
                    </div>
                </section>

                {/* Right Column: Alerts & Logs */}
                <aside className="data-column">
                    <div className="info-blocks">
                        <VehicleInfo vehicle={null} isConnected={!!activeSim} />
                        <AnomalyScore score={activeSim ? (anomalyState === 'attack' ? 92 : anomalyState === 'suspicious' ? 45 : 12) : 0} />
                        <ThreatSummary
                            isActive={anomalyState !== 'normal'}
                            threatType={activeSim?.name || 'Inert State'}
                            confidence={anomalyState === 'attack' ? 'high' : 'medium'}
                            attackVector="TCP/IP Protocol Injection"
                            potentialImpact={[
                                { type: 'Battery Degradation', severity: 'high' },
                                { type: 'Grid Instability', severity: 'medium' }
                            ]}
                        />
                    </div>
                    <div className="scroll-blocks">
                        <LogViewer isRunning={!!activeSim} logs={[]} />
                        <PacketInspector isRunning={!!activeSim} packets={[]} />
                    </div>
                </aside>
            </main>
        </div>
    );
}

export default Dashboard;
