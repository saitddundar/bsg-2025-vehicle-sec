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
import { Play, Square, ChevronDown, ChevronRight, X, Terminal, Zap } from 'lucide-react';
import type { Simulation, SimulationLog } from '../../types';
import './Dashboard.css';

export function Dashboard() {
    const [availableSims, setAvailableSims] = useState<Simulation[] | null>(null);
    const [activeSim, setActiveSim] = useState<Simulation | null>(null);
    const [elapsed, setElapsed] = useState(0);
    const [anomalyState, setAnomalyState] = useState<'normal' | 'suspicious' | 'attack'>('normal');
    const [events, setEvents] = useState<any[]>([]);
    const [logs, setLogs] = useState<SimulationLog[]>([]);
    const [showConsole, setShowConsole] = useState(false);

    const [panels, setPanels] = useState({
        intelligence: true,
        diagnostics: true,
        asset: true,
        eventStream: false
    });
    const [selectedSim, setSelectedSim] = useState<Simulation | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const [voltage, setVoltage] = useState(230);
    const [frequency, setFrequency] = useState(50.0);
    const [v2gPower, setV2gPower] = useState(0);
    const [anomalyScore, setAnomalyScore] = useState(0);


    // Load simulations on mount
    useEffect(() => {
        getSimulations().then(sims => {
            console.log("DEBUG: Fetched simulations in UI", sims);
            setAvailableSims(sims);
        }).catch(err => {
            console.error("DEBUG: Failed to fetch simulations in UI", err);
        });
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
            setVoltage(230);
            setFrequency(50.0);
            setV2gPower(0);
            setAnomalyScore(0);
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
                    await runSimulation(sim.id, sim.scripts[0].name);
                    setActiveSim(sim);


                    // Connect to logs
                    wsRef.current = connectToSimulationLogs(sim.id, (logJson) => {
                        const log: SimulationLog = JSON.parse(logJson);
                        setLogs(prev => [...prev, log].slice(-100));

                        const msgText = log.message;
                        const msg = msgText.toUpperCase();

                        // 1. PHASE DETECTION
                        if (msg.includes('PHASE 1')) {
                            setAnomalyState('normal');
                            pushEvent("STATION: Normal charging handshake initiated", 'system', 'info');
                        } else if (msg.includes('PHASE 2')) {
                            pushEvent("V2G: Bidirectional power flow active", 'system', 'info');
                        } else if (msg.includes('PHASE 3')) {
                            setAnomalyState('attack');
                            pushEvent("SECURITY: V2G Protocol Manipulation Detected!", 'security', 'critical');
                        } else if (msg.includes('PHASE 4')) {
                            setAnomalyState('normal');
                            pushEvent("MITIGATION: Asset isolated, attack blocked", 'action', 'info');
                        }

                        // 2. DETAILED EVENT TRIGGERS
                        if (msg.includes('[ATTACK]')) {
                            setAnomalyState('attack');
                            if (!msg.includes('DETECTED')) {
                                pushEvent(`ALERT: ${msgText.split('[ATTACK]')[1]?.trim() || 'Coordinated V2G attack detected!'}`, 'security', 'critical');
                            }
                        } else if (msg.includes('[CRITICAL]')) {
                            setAnomalyState('attack');
                            pushEvent(`CRITICAL: ${msgText.split('[CRITICAL]')[1]?.trim() || 'System critical state!'}`, 'security', 'critical');
                        } else if (msg.includes('[WARNING]')) {
                            setAnomalyState('suspicious');
                            pushEvent(`WARNING: ${msgText.split('[WARNING]')[1]?.trim() || 'Anomaly detected!'}`, 'security', 'warning');
                        } else if (msg.includes('[GUARD]')) {
                            pushEvent("GUARD: Active defense system deployed", 'action', 'info');
                        } else if (msg.includes('[BLOCKED]')) {
                            pushEvent(`ACTION: ${msgText.split('[BLOCKED]')[1]?.trim() || 'Connection terminated'}`, 'action', 'info');
                        }

                        // 3. STATS PARSING
                        if (msg.includes('[STATS]')) {
                            const rateMatch = msg.match(/\((\d+)%\)/);
                            if (rateMatch) {
                                // Dynamic anomaly rate update logic could go here
                                pushEvent(`DIAGNOSTIC: System Health Check - ${rateMatch[1]}% Anomaly Rate`, 'system', 'info');
                            }
                        }
                        // 3. STATS PARSING
                        if (msg.includes('[STATS]')) {
                            const rateMatch = msg.match(/Anomaly:\s+\d+\s+\((\d+)%\)/i);
                            if (rateMatch) {
                                setAnomalyScore(parseInt(rateMatch[1]));
                            }
                        }

                        // 4. TELEMETRY PARSING
                        if (msg.includes('FREQUENCY:')) {
                            const match = msgText.match(/Frequency:\s+([\d.]+)/i);
                            if (match) setFrequency(parseFloat(match[1]));
                        }
                        if (msg.includes('VOLTAGE:')) {
                            const match = msgText.match(/Voltage:\s+([\d.]+)/i);
                            if (match) setVoltage(parseFloat(match[1]));
                        }
                        if (msg.includes('V2G:')) {
                            const match = msgText.match(/V2G:\s+([-\d.]+)/i);
                            if (match) setV2gPower(parseFloat(match[1]));
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
                            {availableSims && availableSims.length > 0 ? (
                                availableSims.map(sim => (
                                    <div
                                        key={sim.id}
                                        className={`scenario-card-pro ${activeSim?.id === sim.id ? 'active' : ''} ${selectedSim?.id === sim.id ? 'selected' : ''}`}
                                        onClick={() => setSelectedSim(sim)}
                                    >
                                        <div className="card-top">
                                            <span className="scen-name">{sim.name}</span>
                                            {activeSim?.id === sim.id ? <Square size={12} /> : <Play size={12} />}
                                        </div>
                                        <p className="scen-desc">{sim.description}</p>
                                    </div>
                                ))
                            ) : (
                                <div className="empty-state-msg">
                                    {availableSims === null ? 'Loading scenarios...' : 'No active scenarios detected.'}
                                </div>
                            )}

                            {/* Scenario Start/Stop Button */}
                            {selectedSim && (
                                <button
                                    className={`scenario-start-btn ${activeSim?.id === selectedSim.id ? 'running' : ''}`}
                                    onClick={() => handleToggleSim(selectedSim)}
                                >
                                    {activeSim?.id === selectedSim.id ? (
                                        <><Square size={14} /> Stop Simulation</>
                                    ) : (
                                        <><Zap size={14} /> Start Scenario</>
                                    )}
                                </button>
                            )}
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
                            <MetricsChart
                                isRunning={!!activeSim}
                                anomalyState={anomalyState}
                                voltage={voltage}
                                frequency={frequency}
                                power={v2gPower}
                            />
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
                        {panels.diagnostics && <AnomalyScore score={activeSim ? anomalyScore : 0} />}
                    </section>

                    <section className="collapsible-card">
                        <header className="card-header" onClick={() => setPanels(p => ({ ...p, asset: !p.asset }))}>
                            <span className="label">ASSET</span>
                            {panels.asset ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </header>
                        {panels.asset && <VehicleInfo vehicle={null} isConnected={!!activeSim} soc={78} power={v2gPower} />}
                    </section>


                    <button className="console-launcher" onClick={() => setShowConsole(true)}>
                        <Terminal size={14} />
                        <span>OPEN CONSOLE ({logs.length})</span>
                    </button>
                </aside>
            </div>

            <BottomBar events={events} />

            {showConsole && (
                <div className="console-overlay" onClick={() => setShowConsole(false)}>
                    <div className="console-window" onClick={(e) => e.stopPropagation()}>
                        <header className="window-header">
                            <div className="header-title">
                                <Terminal size={14} style={{ marginRight: '8px' }} />
                                SYSTEM CONSOLE & REAL-TIME LOGS
                            </div>
                            <button className="icon-btn-small" onClick={() => setShowConsole(false)}><X size={16} /></button>
                        </header>
                        <div className="window-content">
                            <LogViewer logs={logs.map(l => l.message)} isRunning={!!activeSim} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
