import { useState, useEffect, useMemo } from 'react';
import {
    Shield, Zap,
    Wifi,
    Play, Pause, FileText, Search
} from 'lucide-react';
import {
    AreaChart, Area, ResponsiveContainer,
    XAxis, YAxis, Tooltip, ScatterChart, Scatter, Cell,
    BarChart, Bar
} from 'recharts';
import './DashboardNew.css';
import { scenarioConfigs, generateAnomalyData, generateScenarioLog, generateScenarioTimeSeries } from '../../utils/scenarioData';

// --- Types ---

interface Scenario {
    id: string;
    name: string;
    author: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    status: 'normal' | 'suspicious' | 'attack';
    description?: string;
    anomalyType?: string;
}

interface LogEntry {
    id: string;
    timestamp: string;
    level: 'info' | 'warn' | 'error';
    message: string;
}

// --- Data ---

const scenarios: Scenario[] = scenarioConfigs;

// --- Sub-components ---

const MiniSparkline = ({ color }: { color: string }) => {
    const data = useMemo(() => Array.from({ length: 12 }, () => ({ v: Math.random() * 100 })), []);
    return (
        <div style={{ width: 60, height: 30 }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <Area type="monotone" dataKey="v" stroke={color} fill={color} fillOpacity={0.1} strokeWidth={2} isAnimationActive={false} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

// --- Main Page ---

export function DashboardNew() {
    const [activeTab, setActiveTab] = useState('control');
    const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>('v2g-mod');
    const [isRunning, setIsRunning] = useState(false);
    const [runTime, setRunTime] = useState(0);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [search, setSearch] = useState('');
    const [systemHealth, setSystemHealth] = useState(87);
    const [riskLevel, setRiskLevel] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');

    // Dynamic data based on scenario
    const [anomalyData, setAnomalyData] = useState(generateAnomalyData('v2g-mod', false));
    const [timeSeriesData, setTimeSeriesData] = useState(generateScenarioTimeSeries('v2g-mod', false));
    const [scatterData] = useState(() => Array.from({ length: 50 }, () => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
        z: Math.random() * 10
    })));


    const selectedScenario = useMemo(() => scenarios.find(s => s.id === selectedScenarioId), [selectedScenarioId]);

    // Update scenario-specific data when scenario changes
    useEffect(() => {
        if (selectedScenarioId) {
            // Switch tab to control when scenario changes
            setActiveTab('control');
            // Reset simulation
            setIsRunning(false);
            setRunTime(0);
            setLogs([]);
            // Update data
            setAnomalyData(generateAnomalyData(selectedScenarioId, false));
            setTimeSeriesData(generateScenarioTimeSeries(selectedScenarioId, false));
        }
    }, [selectedScenarioId]);

    // Update risk level based on selected scenario
    useEffect(() => {
        if (selectedScenario) {
            if (selectedScenario.status === 'attack') {
                setRiskLevel('critical');
            } else if (selectedScenario.status === 'suspicious') {
                setRiskLevel('high');
            } else if (selectedScenario.severity === 'critical') {
                setRiskLevel('high');
            } else if (selectedScenario.severity === 'high') {
                setRiskLevel('medium');
            } else {
                setRiskLevel('low');
            }
        }
    }, [selectedScenario]);

    // Timer & Log Simulation with scenario-specific data
    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (isRunning && selectedScenarioId) {
            interval = setInterval(() => {
                setRunTime(t => t + 1);

                // Update anomaly data
                setAnomalyData(generateAnomalyData(selectedScenarioId, true));
                setTimeSeriesData(generateScenarioTimeSeries(selectedScenarioId, true));

                // Generate scenario-specific logs
                if (Math.random() > 0.65) {
                    const message = generateScenarioLog(selectedScenarioId);
                    const isAnomaly = message.includes('⚠️') || message.includes('FAIL') || message.includes('anomaly');
                    const newLog: LogEntry = {
                        id: Math.random().toString(36).substr(2, 9),
                        timestamp: new Date().toLocaleTimeString('en-GB', { hour12: false }),
                        level: isAnomaly ? 'error' : (Math.random() > 0.7 ? 'warn' : 'info'),
                        message
                    };
                    setLogs(prev => [newLog, ...prev].slice(0, 50));
                }

                // Simulate system health changes based on anomaly level
                const healthImpact = anomalyData.energyFlowAnomaly / 10;
                setSystemHealth(prev => Math.max(30, Math.min(100, prev - healthImpact * 0.5 + (Math.random() - 0.3))));
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRunning, selectedScenarioId, anomalyData.energyFlowAnomaly]);

    const formatRunTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const filteredScenarios = useMemo(() => {
        return scenarios.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.author.toLowerCase().includes(search.toLowerCase()));
    }, [search]);

    return (
        <div className="dashboard-container">
            {/* Compact Header */}
            <nav className="dashboard-nav-compact">
                <div className="nav-left">
                    <span className="nav-logo">EV SECURITY</span>
                </div>
                <div className="nav-center">
                    <button className={`nav-item-compact ${activeTab === 'ev' ? 'active' : ''}`} onClick={() => setActiveTab('ev')}>EV/Charging</button>
                    <button className={`nav-item-compact ${activeTab === 'cyber' ? 'active' : ''}`} onClick={() => setActiveTab('cyber')}>Cyber-Physical</button>
                    <button className={`nav-item-compact ${activeTab === 'control' ? 'active' : ''}`} onClick={() => setActiveTab('control')}>Control Central</button>
                    <button className={`nav-item-compact ${activeTab === 'network' ? 'active' : ''}`} onClick={() => setActiveTab('network')}>Network</button>
                    <button className={`nav-item-compact ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>Logs</button>
                </div>
                <div className="nav-right">
                    {selectedScenario && (
                        <div className="header-scenario-info-compact">
                            <span className="header-scenario-name">{selectedScenario.name}</span>
                            <div className={`session-badge-compact ${isRunning ? 'active' : 'standby'}`}>
                                {isRunning ? 'ACTIVE' : 'STANDBY'}
                            </div>
                        </div>
                    )}
                </div>
            </nav>

            <div className="dashboard-main-layout-three-col">
                {/* 1. LEFT: Attack Scenarios (Compact) */}
                <aside className="scenario-sidebar-compact">
                    <div className="sidebar-header-compact">
                        <span className="sidebar-title-compact"><Shield size={12} /> SCENARIOS</span>
                        <span className="sidebar-count">{scenarios.length}</span>
                    </div>
                    <div className="search-container-compact">
                        <Search size={12} className="search-icon" />
                        <input
                            type="text"
                            className="sidebar-search-compact"
                            placeholder="Search..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                    <div className="scenario-list-compact custom-scrollbar">
                        {filteredScenarios.map(s => (
                            <button
                                key={s.id}
                                className={`scenario-card-compact ${selectedScenarioId === s.id ? 'active' : ''}`}
                                onClick={() => setSelectedScenarioId(s.id)}
                            >
                                <div className={`status-led-compact ${s.status}`} />
                                <div className="scenario-info-compact">
                                    <span className={`severity-badge-compact ${s.severity}`}>{s.severity}</span>
                                    <span className="scenario-name-compact">{s.name}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </aside>

                {/* 2. CENTER: Graphics & Animations */}
                <main className="content-area-center">
                    {activeTab === 'control' ? (
                        <div className="control-central-view-compact">
                            {/* V2G Power Grid Visualization */}
                            <div className="v2g-power-grid">
                                {/* Power Grid Node */}
                                <div className="grid-node">
                                    <div className="node-icon-wrapper grid-icon">
                                        <svg viewBox="0 0 40 40" className="node-svg">
                                            <circle cx="20" cy="20" r="18" fill="none" stroke="var(--accent-cyber)" strokeWidth="2" />
                                            <path d="M10 20 L15 12 L20 20 L25 12 L30 20" fill="none" stroke="var(--accent-cyber)" strokeWidth="2" strokeLinecap="round" />
                                            <path d="M10 28 L15 20 L20 28 L25 20 L30 28" fill="none" stroke="var(--accent-cyber)" strokeWidth="2" strokeLinecap="round" />
                                        </svg>
                                    </div>
                                    <span className="node-label">POWER GRID</span>
                                    <span className="node-value">230V / 50Hz</span>
                                </div>

                                {/* Energy Flow Line 1 */}
                                <div className="energy-flow-line">
                                    <div className="flow-track"></div>
                                    <div className={`flow-pulse pulse-1 ${isRunning ? 'active' : ''}`}></div>
                                    <div className={`flow-pulse pulse-2 ${isRunning ? 'active' : ''}`}></div>
                                    <div className={`flow-pulse pulse-3 ${isRunning ? 'active' : ''}`}></div>
                                </div>

                                {/* EVSE Station Node */}
                                <div className="grid-node station-node">
                                    <div className="node-icon-wrapper station-icon">
                                        <svg viewBox="0 0 40 40" className="node-svg">
                                            <rect x="8" y="6" width="24" height="28" rx="3" fill="none" stroke="var(--accent-ev)" strokeWidth="2" />
                                            <rect x="12" y="10" width="16" height="8" rx="1" fill="rgba(255,214,0,0.2)" stroke="var(--accent-ev)" strokeWidth="1" />
                                            <circle cx="20" cy="26" r="4" fill="var(--accent-ev)" className="station-port-glow" />
                                            <text x="20" y="13" textAnchor="middle" fill="var(--accent-ev)" fontSize="4" fontWeight="bold">{systemHealth.toFixed(0)}%</text>
                                        </svg>
                                    </div>
                                    <span className="node-label">EVSE STATION</span>
                                    <span className="node-value">DC 50kW</span>
                                </div>

                                {/* Energy Flow Line 2 */}
                                <div className="energy-flow-line">
                                    <div className="flow-track"></div>
                                    <div className={`flow-pulse pulse-1 ${isRunning ? 'active' : ''}`}></div>
                                    <div className={`flow-pulse pulse-2 ${isRunning ? 'active' : ''}`}></div>
                                    <div className={`flow-pulse pulse-3 ${isRunning ? 'active' : ''}`}></div>
                                </div>

                                {/* Vehicle Node */}
                                <div className="grid-node vehicle-node">
                                    <div className="node-icon-wrapper vehicle-icon">
                                        <svg viewBox="0 0 50 30" className="node-svg vehicle">
                                            <rect x="5" y="8" width="40" height="16" rx="4" fill="var(--accent-ev)" opacity="0.8" />
                                            <rect x="10" y="4" width="30" height="8" rx="2" fill="var(--accent-ev)" opacity="0.6" />
                                            <rect x="13" y="6" width="10" height="4" rx="1" fill="rgba(100,200,255,0.5)" />
                                            <rect x="27" y="6" width="10" height="4" rx="1" fill="rgba(100,200,255,0.5)" />
                                            <circle cx="12" cy="24" r="4" fill="#333" />
                                            <circle cx="38" cy="24" r="4" fill="#333" />
                                        </svg>
                                    </div>
                                    <span className="node-label">ELECTRIC VEHICLE</span>
                                    <span className="node-value">SoC: {systemHealth.toFixed(0)}%</span>
                                </div>
                            </div>

                            {/* Status Metrics Bar */}
                            <div className="status-metrics-bar">
                                <div className="metric-card">
                                    <span className="metric-label">Power Flow</span>
                                    <span className="metric-value">{isRunning ? '48.2' : '0.0'} <small>kW</small></span>
                                </div>
                                <div className="metric-card">
                                    <span className="metric-label">Battery</span>
                                    <div className="battery-indicator">
                                        <div className="battery-fill" style={{ width: `${systemHealth}%` }}></div>
                                    </div>
                                    <span className="metric-value-small">{systemHealth.toFixed(0)}%</span>
                                </div>
                                <div className="metric-card">
                                    <span className="metric-label">Session</span>
                                    <span className="metric-value">{formatRunTime(runTime)}</span>
                                </div>
                                <div className="metric-card status-card">
                                    <div className={`status-indicator-dot ${isRunning ? 'active' : ''}`}></div>
                                    <span className="status-text">{isRunning ? 'CHARGING' : 'STANDBY'}</span>
                                </div>
                            </div>

                            {/* Event Log Section */}
                            <div className="event-log-section">
                                <div className="section-header-small">
                                    <span>SYSTEM EVENTS</span>
                                    <span className="event-count-badge">{logs.length}</span>
                                </div>
                                <div className="event-list-scroll">
                                    {logs.length > 0 ? (
                                        logs.slice(0, 8).map(log => (
                                            <div key={log.id} className={`event-item ${log.level}`}>
                                                <span className="event-time">{log.timestamp}</span>
                                                <span className="event-type">{log.level === 'info' ? 'SYS' : log.level === 'warn' ? 'WARN' : 'ERR'}</span>
                                                <span className="event-msg">{log.message}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="empty-events">
                                            <span>Waiting for events...</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : activeTab === 'ev' ? (
                        <div className="detail-view">
                            <div className="detail-header">
                                <Zap size={24} className="detail-icon ev-icon" />
                                <div>
                                    <h1 className="detail-title">EV & CHARGING</h1>
                                    <p className="detail-subtitle">Energy Logic & VPP Integration</p>
                                </div>
                            </div>
                            <div className="detail-content">
                                <div className="detail-chart-container">
                                    <span className="mini-box-label">Energy Flow Timeline</span>
                                    <ResponsiveContainer width="100%" height="90%">
                                        <AreaChart data={timeSeriesData}>
                                            <defs>
                                                <linearGradient id="evGradient" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="var(--accent-ev)" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="var(--accent-ev)" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <XAxis dataKey="time" />
                                            <YAxis />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="soc" stroke="var(--accent-ev)" strokeWidth={3} fillOpacity={1} fill="url(#evGradient)" />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    ) : activeTab === 'cyber' ? (
                        <div className="detail-view">
                            <div className="detail-header">
                                <Shield size={24} className="detail-icon cyber-icon" />
                                <div>
                                    <h1 className="detail-title">CYBER-PHYSICAL</h1>
                                    <p className="detail-subtitle">Sensor Consistency & Verification</p>
                                </div>
                            </div>
                            <div className="detail-content">
                                <div className="detail-chart-container">
                                    <span className="mini-box-label">Cross-Sensor Correlation</span>
                                    <ResponsiveContainer width="100%" height="90%">
                                        <ScatterChart>
                                            <XAxis type="number" dataKey="x" name="x" hide />
                                            <YAxis type="number" dataKey="y" name="y" hide />
                                            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                                            <Scatter name="Telemetry" data={scatterData} fill="var(--accent-cyber)">
                                                {scatterData.map((_: any, index: number) => (
                                                    <Cell key={`cell-${index}`} fill={index % 10 === 0 ? 'var(--status-danger)' : 'var(--accent-cyber)'} />
                                                ))}
                                            </Scatter>
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    ) : activeTab === 'network' ? (
                        <div className="detail-view">
                            <div className="detail-header">
                                <Wifi size={24} className="detail-icon network-icon" />
                                <div>
                                    <h1 className="detail-title">NETWORK</h1>
                                    <p className="detail-subtitle">Protocol Analysis & Monitoring</p>
                                </div>
                            </div>
                            <div className="detail-content">
                                <div className="detail-chart-container">
                                    <span className="mini-box-label">Network Traffic Distribution</span>
                                    <ResponsiveContainer width="100%" height="90%">
                                        <BarChart data={timeSeriesData.slice(0, 8)}>
                                            <XAxis dataKey="time" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar dataKey="value" fill="var(--bg-hover)" />
                                            <Bar dataKey="anomalous" fill="var(--status-danger)" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    ) : activeTab === 'logs' ? (
                        <div className="detail-view">
                            <div className="detail-header">
                                <FileText size={24} className="detail-icon" />
                                <div>
                                    <h1 className="detail-title">SYSTEM LOGS</h1>
                                    <p className="detail-subtitle">Real-time Event Logging</p>
                                </div>
                            </div>
                            <div className="detail-content">
                                <div className="logs-container custom-scrollbar">
                                    {logs.length > 0 ? (
                                        logs.map(l => (
                                            <div key={l.id} className="log-entry">
                                                <span className="log-timestamp">{l.timestamp}</span>
                                                <span className={`log-level ${l.level}`}>{l.level.toUpperCase()}</span>
                                                <span className="log-message">{l.message}</span>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="logs-empty">No logs available</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="empty-state-center">
                            <div className="empty-icon"><Shield size={64} style={{ color: 'var(--accent-primary)', opacity: 0.4 }} /></div>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, textTransform: 'uppercase' }}>Select a Scenario</h2>
                            <p style={{ maxWidth: '400px', fontSize: '0.9rem', color: 'var(--text-dim)' }}>
                                Choose an attack scenario from the left panel to begin analysis.
                            </p>
                        </div>
                    )}
                </main>

                {/* 3. RIGHT: Data Panel */}
                <aside className="data-panel">
                    <div className="data-panel-header">
                        <span className="data-panel-title">SYSTEM DATA</span>
                    </div>
                    <div className="data-panel-content custom-scrollbar">
                        {/* System Status */}
                        <div className="data-section">
                            <div className="data-section-header">
                                <span className="data-section-title">STATUS</span>
                            </div>
                            <div className="data-metrics-grid">
                                <div className="data-metric-item">
                                    <span className="data-metric-label">Risk Level</span>
                                    <div className={`risk-indicator-small ${riskLevel}`}>
                                        <div className="risk-pulse-small" />
                                        <span className="risk-text-small">{riskLevel.toUpperCase()}</span>
                                    </div>
                                </div>
                                <div className="data-metric-item">
                                    <span className="data-metric-label">Uptime</span>
                                    <span className="data-metric-value">{formatRunTime(runTime)}</span>
                                </div>
                                <div className="data-metric-item">
                                    <span className="data-metric-label">Health</span>
                                    <span className="data-metric-value">{systemHealth.toFixed(1)}%</span>
                                </div>
                                <div className="data-metric-item">
                                    <span className="data-metric-label">Active Threats</span>
                                    <span className="data-metric-value">{selectedScenario?.status === 'attack' ? '1' : '0'}</span>
                                </div>
                            </div>
                        </div>

                        {/* EV Metrics */}
                        <div className="data-section">
                            <div className="data-section-header">
                                <Zap size={14} className="data-section-icon ev-icon" />
                                <span className="data-section-title">EV & CHARGING</span>
                            </div>
                            <div className="data-metrics-list">
                                <div className="data-metric-row">
                                    <span className="data-metric-label">State of Charge</span>
                                    <span className="data-metric-value-large">67<span className="data-metric-unit">%</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">VPP Power Flow</span>
                                    <span className="data-metric-value-large">2.4<span className="data-metric-unit">kW</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Charging Rate</span>
                                    <span className="data-metric-value-large">7.2<span className="data-metric-unit">kW</span></span>
                                </div>
                            </div>
                        </div>

                        {/* Cyber-Physical Metrics */}
                        <div className="data-section">
                            <div className="data-section-header">
                                <Shield size={14} className="data-section-icon cyber-icon" />
                                <span className="data-section-title">CYBER-PHYSICAL</span>
                            </div>
                            <div className="data-metrics-list">
                                <div className="data-metric-row">
                                    <span className="data-metric-label">GPS Verification</span>
                                    <div className="data-status">
                                        <div className={`status-dot-small ${anomalyData.gpsDeviation > 5 ? 'danger' : 'success'}`} />
                                        <span className="data-status-text">{anomalyData.gpsDeviation > 5 ? 'DEVIATION' : 'MATCHED'}</span>
                                    </div>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">CAN Bus Integrity</span>
                                    <div className="data-status">
                                        <div className={`status-dot-small ${anomalyData.canBusError ? 'danger' : 'success'}`} />
                                        <span className="data-status-text">{anomalyData.canBusError ? 'ERROR' : 'SECURE'}</span>
                                    </div>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Firmware Hash</span>
                                    <div className="data-status">
                                        <div className={`status-dot-small ${anomalyData.firmwareHash === 'invalid' ? 'danger' : (anomalyData.firmwareHash === 'pending' ? 'warning' : 'success')}`} />
                                        <span className="data-status-text">{anomalyData.firmwareHash.toUpperCase()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Network Metrics */}
                        <div className="data-section">
                            <div className="data-section-header">
                                <Wifi size={14} className="data-section-icon network-icon" />
                                <span className="data-section-title">NETWORK</span>
                            </div>
                            <div className="data-metrics-list">
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Latency</span>
                                    <span className="data-metric-value">{anomalyData.networkLatency.toFixed(0)}<span className="data-metric-unit">ms</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Throughput</span>
                                    <span className="data-metric-value">1.4<span className="data-metric-unit">MB/s</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Packet Loss</span>
                                    <span className="data-metric-value">{anomalyData.packetLoss.toFixed(2)}<span className="data-metric-unit">%</span></span>
                                </div>
                            </div>
                        </div>

                        {/* Control Actions */}
                        <div className="data-section">
                            <div className="data-section-header">
                                <span className="data-section-title">CONTROLS</span>
                            </div>
                            <div className="data-actions">
                                <button
                                    className={`data-action-btn ${isRunning ? 'btn-pause' : 'btn-start'}`}
                                    onClick={() => setIsRunning(!isRunning)}
                                >
                                    {isRunning ? <><Pause size={16} /> PAUSE</> : <><Play size={16} /> DEPLOY</>}
                                </button>
                                <button className="data-action-btn btn-secondary">
                                    <FileText size={16} /> EXPORT
                                </button>
                            </div>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    );
}

export default DashboardNew;
