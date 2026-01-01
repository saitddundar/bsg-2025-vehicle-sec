import { useState, useEffect, useMemo } from 'react';
import {
    Activity, Shield, Zap,
    Wifi,
    Play, Pause, FileText, Search
} from 'lucide-react';
import {
    AreaChart, Area, ResponsiveContainer,
    XAxis, YAxis, Tooltip, ScatterChart, Scatter, Cell,
    BarChart, Bar
} from 'recharts';
import './DashboardNew.css';

// --- Types ---

interface Scenario {
    id: string;
    name: string;
    author: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    status: 'normal' | 'suspicious' | 'attack';
}

interface LogEntry {
    id: string;
    timestamp: string;
    level: 'info' | 'warn' | 'error';
    message: string;
}

// --- Mock Data ---

const scenarios: Scenario[] = [
    { id: 'v2g-mod', name: 'V2G Protocol Manipulation', author: 'Sait Dundar', severity: 'critical', status: 'attack' },
    { id: 'phantom-soc', name: 'Phantom SoC Report', author: 'Kardelen Demir', severity: 'high', status: 'suspicious' },
    { id: 'firmware-pdos', name: 'Firmware P-DoS Attack', author: 'Betül Altunyuva', severity: 'critical', status: 'normal' },
    { id: 'ocpp-stealth', name: 'OCPP Stealth Beaconing', author: 'Göksu Kayar', severity: 'high', status: 'normal' },
    { id: 'digital-twin', name: 'Digital Twin Spoofing', author: 'Mehmet Erdem Abacı', severity: 'medium', status: 'normal' },
    { id: 'siren-attack', name: 'Siren Attack', author: 'BSG Team', severity: 'critical', status: 'normal' },
    { id: 'disp-manip', name: 'Display Manipulation', author: 'BSG Team', severity: 'medium', status: 'normal' },
    { id: 'charge-move', name: 'Charging While Moving', author: 'BSG Team', severity: 'high', status: 'normal' },
    { id: 'ghost-ecu', name: 'Ghost ECU Injection', author: 'BSG Team', severity: 'critical', status: 'normal' },
];

const mockTimeSeries = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    value: Math.floor(Math.random() * 50) + 100,
    anomalous: Math.random() > 0.8 ? Math.floor(Math.random() * 20) : 0,
    soc: 80 - i * 0.5 + (Math.random() - 0.5) * 2
}));

const mockScatterData = Array.from({ length: 50 }, () => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    z: Math.random() * 10
}));

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
    const [eventStreamExpanded, setEventStreamExpanded] = useState(false);

    const selectedScenario = useMemo(() => scenarios.find(s => s.id === selectedScenarioId), [selectedScenarioId]);

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

    // Timer & Log Simulation
    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (isRunning) {
            interval = setInterval(() => {
                setRunTime(t => t + 1);
                // Simulate periodic logs
                if (Math.random() > 0.7) {
                    const messages = [
                        "V2G packet received [SAP_0x42]",
                        "Consistency check passed for CPU_0",
                        "Heartbeat stable @ 10Hz",
                        "Encryption handshake complete",
                        "New session token generated"
                    ];
                    addLog(messages[Math.floor(Math.random() * messages.length)], 'info');
                    if (logs.length > 0 && !eventStreamExpanded) {
                        setEventStreamExpanded(true);
                    }
                }
                // Simulate system health changes
                setSystemHealth(prev => Math.max(50, Math.min(100, prev + (Math.random() - 0.5) * 2)));
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRunning, logs.length, eventStreamExpanded]);

    const formatRunTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const filteredScenarios = useMemo(() => {
        return scenarios.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.author.toLowerCase().includes(search.toLowerCase()));
    }, [search]);

    const addLog = (message: string, level: 'info' | 'warn' | 'error' = 'info') => {
        const newLog: LogEntry = {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toLocaleTimeString('en-GB', { hour12: false }),
            level,
            message
        };
        setLogs(prev => [newLog, ...prev].slice(0, 50));
    };

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
                            {/* System State Core - Centered */}
                            <div className="system-state-core-center">
                                <div className="core-container">
                                    <div className="core-ring outer-ring" />
                                    <div className="core-ring middle-ring" />
                                    <div className="core-inner">
                                        <div className="core-value">{systemHealth}</div>
                                        <div className="core-label">SYSTEM HEALTH</div>
                                        <div className="core-status">
                                            <div className={`core-status-dot ${systemHealth > 80 ? 'healthy' : systemHealth > 60 ? 'warning' : 'critical'}`} />
                                            <span>{systemHealth > 80 ? 'OPERATIONAL' : systemHealth > 60 ? 'DEGRADED' : 'CRITICAL'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Charts Section */}
                            <div className="charts-section">
                                <div className="chart-card">
                                    <div className="chart-header">
                                        <Zap size={16} className="chart-icon ev-icon" />
                                        <span className="chart-title">Energy Flow</span>
                                    </div>
                                    <div className="chart-body">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={mockTimeSeries.slice(0, 12)}>
                                                <defs>
                                                    <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="var(--accent-ev)" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="var(--accent-ev)" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <XAxis dataKey="time" hide />
                                                <YAxis hide />
                                                <Tooltip />
                                                <Area type="monotone" dataKey="soc" stroke="var(--accent-ev)" strokeWidth={2} fillOpacity={1} fill="url(#energyGradient)" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>

                            {/* Event Stream - Collapsible */}
                            <div className={`event-stream-timeline-compact ${eventStreamExpanded || logs.length > 0 ? 'expanded' : 'collapsed'}`}>
                                <div className="event-stream-header-compact" onClick={() => setEventStreamExpanded(!eventStreamExpanded)}>
                                    <div className="stream-header-left">
                                        <Activity size={14} />
                                        <span>EVENT STREAM</span>
                                        {logs.length > 0 && <span className="event-count">({logs.length})</span>}
                                    </div>
                                    <div className="stream-header-right">
                                        <div className={`live-indicator ${isRunning ? 'active' : ''}`} />
                                        <span className="live-text">{isRunning ? 'LIVE' : 'STANDBY'}</span>
                                    </div>
                                </div>
                                {(eventStreamExpanded || logs.length > 0) && (
                                    <div className="event-stream-content-compact custom-scrollbar">
                                        {logs.length > 0 ? (
                                            logs.map(l => (
                                                <div key={l.id} className="event-log-row-compact">
                                                    <span className="event-timestamp">{l.timestamp}</span>
                                                    <span className={`event-source ${l.level}`}>
                                                        {l.level === 'info' ? 'SYS' : l.level === 'warn' ? 'IDS' : 'FIREWALL'}
                                                    </span>
                                                    <span className="event-message">{l.message}</span>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="event-stream-empty">
                                                <Activity size={24} style={{ opacity: 0.3 }} />
                                                <span>Waiting for telemetry...</span>
                                            </div>
                                        )}
                                    </div>
                                )}
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
                                        <AreaChart data={mockTimeSeries}>
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
                                            <Scatter name="Telemetry" data={mockScatterData} fill="var(--accent-cyber)">
                                                {mockScatterData.map((_, index) => (
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
                                        <BarChart data={mockTimeSeries.slice(0, 8)}>
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
                                <Activity size={24} className="detail-icon" />
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
                                        <div className="status-dot-small success" />
                                        <span className="data-status-text">MATCHED</span>
                                    </div>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">CAN Bus Integrity</span>
                                    <div className="data-status">
                                        <div className="status-dot-small success" />
                                        <span className="data-status-text">SECURE</span>
                                    </div>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Firmware Hash</span>
                                    <div className="data-status">
                                        <div className="status-dot-small warning" />
                                        <span className="data-status-text">PENDING</span>
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
                                    <span className="data-metric-value">42<span className="data-metric-unit">ms</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Throughput</span>
                                    <span className="data-metric-value">1.4<span className="data-metric-unit">MB/s</span></span>
                                </div>
                                <div className="data-metric-row">
                                    <span className="data-metric-label">Packet Loss</span>
                                    <span className="data-metric-value">0.02<span className="data-metric-unit">%</span></span>
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
