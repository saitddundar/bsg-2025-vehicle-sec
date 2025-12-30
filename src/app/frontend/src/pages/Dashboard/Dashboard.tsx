import { useState, useEffect, useRef } from 'react';
import {
    Header,
    VehicleInfo,
    LogViewer,
    NetworkTopology,
    AnomalyScore,
    MetricsChart,
    ThreatSummary,
    AttackTimeline,
    BottomBar,
} from '../../components';
import {
    getSimulations,
    runSimulation,
    stopSimulation,
    connectToSimulationLogs
} from '../../services/simulationService';
import { Play, Square, ChevronDown, ChevronRight, X, Terminal } from 'lucide-react';
import type { Simulation, SimulationLog } from '../../types';
import './Dashboard.css';

export function Dashboard() {
    const [availableSims, setAvailableSims] = useState<Simulation[]>([]);
    const [activeSim, setActiveSim] = useState<Simulation | null>(null);
    const [elapsed, setElapsed] = useState(0);
    const [anomalyState, setAnomalyState] = useState<'normal' | 'suspicious' | 'attack'>('normal');
    const [events, setEvents] = useState<any[]>([]);
    const [logs, setLogs] = useState<SimulationLog[]>([]);
    const [showConsole, setShowConsole] = useState(false);

    const [panels, setPanels] = useState({
        intelligence: true,
        diagnostics: true,
        asset: true
    });

    const wsRef = useRef<WebSocket | null>(null);

    // Load simulations on mount
    useEffect(() => {
        getSimulations().then(setAvailableSims).catch(console.error);
    }, []);

    // Timer logic for active simulation
    useEffect(() => {
        let timer: any;
        if (activeSim) {
            timer = setInterval(() => setElapsed(e => e + 1), 1000);
        } else {
            setElapsed(0);
            setAnomalyState('normal');
            setEvents([]);
            setLogs([]);
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        }
        return () => clearInterval(timer);
    }, [activeSim]);

    const pushEvent = (msg: string, type: 'security' | 'system' | 'action', severity: 'info' | 'warning' | 'critical') => {
        const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
        setEvents(prev => [{ id: Date.now(), time, type, message: msg, severity }, ...prev].slice(0, 10));
    };

    const handleToggleSim = async (sim: Simulation) => {
        if (activeSim?.id === sim.id) {
            await stopSimulation(sim.id);
            setActiveSim(null);
        } else {
            try {
                // Start the first script found in the simulation
                if (sim.scripts.length > 0) {
                    const result = await runSimulation(sim.id, sim.scripts[0].name);
                    setActiveSim(sim);

                    // Connect to logs
                    wsRef.current = connectToSimulationLogs(sim.id, (logJson) => {
                        const log: SimulationLog = JSON.parse(logJson);
                        setLogs(prev => [...prev, log].slice(-100));

                        // Auto-detect anomaly state from logs
                        const msg = log.message.toUpperCase();
                        if (msg.includes('[ATTACK]') || msg.includes('PHASE 3')) {
                            setAnomalyState('attack');
                            pushEvent("CRITICAL: Attack sequence initiated", 'security', 'critical');
                        } else if (msg.includes('[WARNING]') || msg.includes('[CRITICAL]') || msg.includes('ANOMALY')) {
                            setAnomalyState('suspicious');
                            pushEvent("WARNING: System anomaly detected", 'security', 'warning');
                        } else if (msg.includes('[OK]') || msg.includes('PHASE 4') || msg.includes('NORMAL')) {
                            if (anomalyState !== 'normal') {
                                setAnomalyState('normal');
                                pushEvent("SYSTEM: Parameters stabilized", 'system', 'info');
                            }
                        }
                    });

                    pushEvent(`Simulation ${sim.name} started`, 'action', 'info');
                }
            } catch (err) {
                console.error("Failed to start simulation:", err);
            }
        }
    };


    return (
        <div className={`dashboard-professional state-${anomalyState}`}>
            <Header activeSimulation={activeSim?.name} anomalyState={anomalyState} elapsedTime={elapsed} />

            <div className="dashboard-grid-container">
                <aside className="grid-sidebar">
                    <section className="sidebar-section scenarios-fixed">
                        <header className="section-header">
                            <span className="label">ATTACK SCENARIOS</span>
                        </header>
                        <div className="scenario-limited-list">
                            {availableSims.map(sim => (
                                <button
                                    key={sim.id}
                                    className={`scenario-card-pro ${activeSim?.id === sim.id ? 'active' : ''}`}
                                    onClick={() => handleToggleSim(sim)}
                                >
                                    <div className="card-top">
                                        <span className="scen-name">{sim.name}</span>
                                        {activeSim?.id === sim.id ? <Square size={12} fill="currentColor" /> : <Play size={12} />}
                                    </div>
                                    <p className="scen-desc">{sim.description}</p>
                                </button>
                            ))}

                        </div>
                    </section>

                    <section className="sidebar-section kill-chain-box">
                        <header className="section-header">
                            <span className="label">KILL CHAIN TRACKING</span>
                        </header>
                        <div className="kill-chain-scroll">
                            <AttackTimeline
                                recon={elapsed > 5 || anomalyState !== 'normal'}
                                injection={anomalyState === 'attack'}
                                detection={anomalyState === 'attack'}
                            />
                        </div>
                    </section>
                </aside>

                <main className="grid-main scrollable-center">
                    <div className="main-section network-arch">
                        <div className="box-header">
                            <span className="label">NETWORK ARCHITECTURE</span>
                        </div>
                        <div className="box-body">
                            <NetworkTopology
                                vehicleStatus={anomalyState === 'attack' ? 'attack' : 'normal'}
                                evseStatus={anomalyState === 'suspicious' ? 'warning' : 'normal'}
                                csmsStatus="normal"
                                connectionStatus={anomalyState === 'normal' ? 'secure' : 'compromised'}
                                attackerPresent={anomalyState !== 'normal'}
                                flowDirection={activeSim ? (anomalyState === 'attack' ? 'discharging' : 'charging') : 'idle'}
                            />
                        </div>
                    </div>

                    <div className="main-section telemetry-analysis">
                        <div className="box-header">
                            <span className="label">LIVE PARAMETER ANALYSIS</span>
                        </div>
                        <div className="box-body">
                            <MetricsChart isRunning={!!activeSim} anomalyState={anomalyState} />
                        </div>
                    </div>
                </main>

                <aside className="grid-analytics">
                    <section className="collapsible-card">
                        <header className="card-header" onClick={() => setPanels(p => ({ ...p, intelligence: !p.intelligence }))}>
                            <span className="label">INTELLIGENCE</span>
                            {panels.intelligence ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </header>
                        {panels.intelligence && <ThreatSummary isActive={anomalyState !== 'normal'} threatType={activeSim?.name || ''} confidence="high" attackVector="Injection" potentialImpact={[]} />}
                    </section>

                    <section className="collapsible-card">
                        <header className="card-header" onClick={() => setPanels(p => ({ ...p, diagnostics: !p.diagnostics }))}>
                            <span className="label">DIAGNOSTICS</span>
                            {panels.diagnostics ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </header>
                        {panels.diagnostics && <AnomalyScore score={activeSim ? (anomalyState === 'attack' ? 92 : anomalyState === 'suspicious' ? 45 : 12) : 0} />}
                    </section>

                    <section className="collapsible-card">
                        <header className="card-header" onClick={() => setPanels(p => ({ ...p, asset: !p.asset }))}>
                            <span className="label">ASSET</span>
                            {panels.asset ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </header>
                        {panels.asset && <VehicleInfo vehicle={null} isConnected={!!activeSim} />}
                    </section>

                    <button className="console-launcher" onClick={() => setShowConsole(true)}>
                        <Terminal size={14} />
                        <span>OPEN CONSOLE ({logs.length})</span>
                    </button>
                </aside>
            </div>

            <BottomBar events={events} />

            {showConsole && (
                <div className="console-overlay">
                    <div className="console-window">
                        <header className="window-header">
                            <div className="header-title">SYSTEM CONSOLE & REAL-TIME LOGS</div>
                            <button onClick={() => setShowConsole(false)}><X size={16} /></button>
                        </header>
                        <div className="window-content">
                            <LogViewer isRunning={!!activeSim} logs={logs.map(l => l.message)} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
