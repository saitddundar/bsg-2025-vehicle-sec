import { useState, useEffect, useMemo } from 'react';
import {
    Activity, Shield, Zap, CheckCircle,
    Wifi,
    Play, Pause, FileText, Search, X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
    const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [runTime, setRunTime] = useState(0);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [search, setSearch] = useState('');
    const [detailPanel, setDetailPanel] = useState<string | null>(null);

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
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRunning]);

    const formatRunTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const selectedScenario = useMemo(() => scenarios.find(s => s.id === selectedScenarioId), [selectedScenarioId]);

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
            {/* Nav */}
            <nav className="dashboard-nav">
                <button className={`nav-item ${activeTab === 'ev' ? 'active' : ''}`} onClick={() => setActiveTab('ev')}>EV/Charging</button>
                <button className={`nav-item ${activeTab === 'cyber' ? 'active' : ''}`} onClick={() => setActiveTab('cyber')}>Cyber-Physical</button>
                <button className={`nav-center-btn ${activeTab === 'control' ? 'active' : ''}`} onClick={() => setActiveTab('control')}>Control Central</button>
                <button className={`nav-item ${activeTab === 'network' ? 'active' : ''}`} onClick={() => setActiveTab('network')}>Network</button>
                <button className={`nav-item ${activeTab === 'logs' ? 'active' : ''}`} onClick={() => setActiveTab('logs')}>Logs</button>
            </nav>

            <div className="dashboard-main-layout">
                {/* 1. SIDEBAR */}
                <aside className="scenario-sidebar">
                    <div className="sidebar-header">
                        <div className="sidebar-header-top">
                            <span className="sidebar-title"><Shield size={14} /> Attack Scenarios</span>
                            <span style={{ fontSize: '0.65rem' }}>TOTAL: {scenarios.length}</span>
                        </div>
                        <div className="search-container">
                            <Search size={14} className="search-icon" />
                            <input
                                type="text"
                                className="sidebar-search"
                                placeholder="Filter scenarios..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="scenario-list custom-scrollbar">
                        {filteredScenarios.map(s => (
                            <button
                                key={s.id}
                                className={`scenario-card ${selectedScenarioId === s.id ? 'active' : ''}`}
                                onClick={() => setSelectedScenarioId(s.id)}
                            >
                                <div className="scenario-info-left">
                                    <div className="scenario-top-row">
                                        <span className={`severity-badge ${s.severity}`}>{s.severity}</span>
                                        <span className="scenario-name">{s.name}</span>
                                    </div>
                                    <span className="scenario-author">{s.author}</span>
                                </div>
                                <div className={`status-led ${s.status}`} />
                            </button>
                        ))}
                    </div>
                </aside>

                {/* 2. MAIN CONTENT */}
                <main className="content-area">
                    {selectedScenario ? (
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={selectedScenario.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex-1 flex flex-col overflow-hidden"
                            >
                                {/* Sticky Header */}
                                <header className="sticky-header">
                                    <div className="header-scenario-info">
                                        <h1>{selectedScenario.name}</h1>
                                        <div className={`session-badge ${isRunning ? 'active' : 'standby'}`}>
                                            {isRunning ? 'active simulation' : 'ready to deploy'}
                                        </div>
                                    </div>

                                    <div className="header-kpis">
                                        <div className="kpi-group">
                                            <span className="kpi-label">Risk Vector</span>
                                            <span className="kpi-value risk">{selectedScenario.severity}</span>
                                        </div>
                                        <div style={{ width: '1px', height: '24px', background: 'var(--border-subtle)' }} />
                                        <div className="kpi-group">
                                            <span className="kpi-label">Uptime</span>
                                            <span className="kpi-value">{formatRunTime(runTime)}</span>
                                        </div>
                                        <div style={{ width: '1px', height: '24px', background: 'var(--border-subtle)' }} />
                                        <div className="kpi-group">
                                            <span className="kpi-label">Active Alerts</span>
                                            <span className="kpi-value">0</span>
                                        </div>
                                    </div>

                                    <div className="header-actions">
                                        <button
                                            className={`btn-primary ${isRunning ? 'btn-pause' : 'btn-start'}`}
                                            onClick={() => setIsRunning(!isRunning)}
                                        >
                                            {isRunning ? <><Pause size={18} fill="currentColor" /> PAUSE</> : <><Play size={18} fill="currentColor" /> DEPLOY</>}
                                        </button>
                                        <button className="btn-primary btn-secondary">
                                            <FileText size={18} /> EXPORT
                                        </button>
                                    </div>
                                </header>

                                {/* Overview Scroll Content */}
                                <div className="overview-scroll custom-scrollbar">
                                    <div className="category-grid">
                                        {/* EV WIDGET */}
                                        <div className="category-widget ev" onClick={() => setDetailPanel('ev')}>
                                            <div className="widget-left">
                                                <div className="widget-left-icon"><Zap size={20} /></div>
                                            </div>
                                            <div className="widget-content">
                                                <div className="widget-title">EV & Charging</div>
                                                <div className="widget-subtitle">Energy Logic & VPP</div>

                                                <div className="metrics-row">
                                                    <div className="metric-box">
                                                        <span className="m-label">Current SoC</span>
                                                        <div><span className="m-value">67</span><span className="m-unit">%</span></div>
                                                        <div style={{ height: 20, marginTop: 4, opacity: 0.8 }}><MiniSparkline color="var(--accent-ev)" /></div>
                                                    </div>
                                                    <div className="metric-box">
                                                        <span className="m-label">VPP Flux</span>
                                                        <div><span className="m-value">2.4</span><span className="m-unit">kW</span></div>
                                                        <div style={{ height: 20, marginTop: 4, opacity: 0.8 }}><MiniSparkline color="#00FF94" /></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* CYBER WIDGET */}
                                        <div className="category-widget cyber" onClick={() => setDetailPanel('cyber')}>
                                            {selectedScenario.severity === 'critical' && <div className="pulse-alarm" />}
                                            <div className="widget-left">
                                                <div className="widget-left-icon"><Shield size={20} /></div>
                                            </div>
                                            <div className="widget-content">
                                                <div className="widget-title">Cyber-Physical</div>
                                                <div className="widget-subtitle">Sensor Consistency</div>

                                                <div className="metrics-row">
                                                    <div className="metric-box" style={{ gridColumn: 'span 2' }}>
                                                        <span className="m-label">GPS vs CSMS Verif</span>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                                                            <div className="status-led normal" style={{ background: 'var(--status-success)', opacity: 1, boxShadow: '0 0 8px var(--status-success)' }} />
                                                            <span className="m-value">MATCHED</span>
                                                            <span className="m-unit">[Station_042]</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* NETWORK WIDGET */}
                                        <div className="category-widget network" onClick={() => setDetailPanel('network')}>
                                            <div className="widget-left">
                                                <div className="widget-left-icon"><Wifi size={20} /></div>
                                            </div>
                                            <div className="widget-content">
                                                <div className="widget-title">Network</div>
                                                <div className="widget-subtitle">Protocol Analysis</div>

                                                <div className="metrics-row">
                                                    <div className="metric-box">
                                                        <span className="m-label">Latency</span>
                                                        <div><span className="m-value">42</span><span className="m-unit">ms</span></div>
                                                    </div>
                                                    <div className="metric-box">
                                                        <span className="m-label">Throughput</span>
                                                        <div><span className="m-value">1.4</span><span className="m-unit">MB/s</span></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Event Stream Panel */}
                                    <section className="event-stream-section">
                                        <div className="stream-header">
                                            <div className="stream-title">
                                                <Activity size={14} color="var(--accent-primary)" />
                                                <span>Mission Control Event Stream</span>
                                            </div>
                                            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--status-success)', boxShadow: '0 0 8px var(--status-success)' }} />
                                                    <span style={{ fontSize: '0.7rem', color: 'var(--status-success)', fontWeight: 700 }}>LIVE</span>
                                                </div>
                                                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>// REPLAY READY</span>
                                            </div>
                                        </div>
                                        <div className="stream-table custom-scrollbar">
                                            {logs.length > 0 ? logs.map(l => (
                                                <div key={l.id} className="log-row">
                                                    <span className="log-ts">{l.timestamp}</span>
                                                    <span className="log-src" style={{ color: l.level === 'warn' ? 'var(--status-warning)' : l.level === 'error' ? 'var(--status-danger)' : 'var(--accent-primary)' }}>
                                                        {l.level === 'info' ? 'SYS_KERNEL' : l.level === 'warn' ? 'IDS_ALERT' : 'FIREWALL'}
                                                    </span>
                                                    <span className="log-msg">{l.message}</span>
                                                </div>
                                            )) : (
                                                <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.3, flexDirection: 'column', gap: 12 }}>
                                                    <Activity size={32} />
                                                    <span>Waiting for mission telemetry...</span>
                                                </div>
                                            )}
                                        </div>
                                    </section>
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    ) : (
                        <div className="empty-state">
                            <div className="empty-icon"><Shield size={64} style={{ color: 'var(--accent-primary)', opacity: 0.4 }} /></div>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 900, textTransform: 'uppercase' }}>Command Center Ready</h2>
                            <p style={{ maxWidth: '400px', fontSize: '0.9rem', color: 'var(--text-dim)' }}>
                                Select an attack scenario from the left perimeter to begin protocol investigation and real-time anomaly tracking.
                            </p>
                            <div style={{ marginTop: '20px', display: 'flex', gap: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><CheckCircle size={14} style={{ color: 'var(--accent-success)' }} /> SECURE_ENV: UP</span>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><CheckCircle size={14} style={{ color: 'var(--accent-success)' }} /> DB_LINK: ACTIVE</span>
                            </div>
                        </div>
                    )}
                </main>
            </div>

            {/* SLIDE-OVER PANEL */}
            <AnimatePresence>
                {detailPanel && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="slide-over-mask"
                            onClick={() => setDetailPanel(null)}
                        />
                        <motion.aside
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="slide-panel"
                        >
                            <header className="slide-header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                    <div className={`widget-icon ${detailPanel}`}>
                                        {detailPanel === 'ev' && <Zap size={24} />}
                                        {detailPanel === 'cyber' && <Shield size={24} />}
                                        {detailPanel === 'network' && <Wifi size={24} />}
                                    </div>
                                    <div>
                                        <h2 style={{ fontWeight: 900, textTransform: 'uppercase', letterSpacing: '1px' }}>
                                            {detailPanel === 'ev' && 'Energy Matrix'}
                                            {detailPanel === 'cyber' && 'Consistency Engine'}
                                            {detailPanel === 'network' && 'Protocol Inspector'}
                                        </h2>
                                        <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Real-time Deep Packet Correlation</p>
                                    </div>
                                </div>
                                <button onClick={() => setDetailPanel(null)} className="nav-item"><X size={24} /></button>
                            </header>

                            <div className="slide-body custom-scrollbar">
                                {/* Sample Chart 1: Time Series */}
                                <div className="detail-chart-container">
                                    <span className="mini-box-label">Spectral Flux Timeline</span>
                                    <ResponsiveContainer width="100%" height="90%">
                                        <AreaChart data={mockTimeSeries}>
                                            <defs>
                                                <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="var(--accent-primary)" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="var(--accent-primary)" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <XAxis dataKey="time" hide />
                                            <YAxis hide />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="value" stroke="var(--accent-primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorVal)" />
                                            {isRunning && <Area type="monotone" dataKey="anomalous" stroke="var(--accent-danger)" fill="var(--accent-danger)" fillOpacity={0.2} />}
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>

                                {/* Sample Chart 2: Correlation Scatter / Bar */}
                                {detailPanel === 'cyber' ? (
                                    <div className="detail-chart-container">
                                        <span className="mini-box-label">Cross-Sensor Correlation Map</span>
                                        <ResponsiveContainer width="100%" height="90%">
                                            <ScatterChart>
                                                <XAxis type="number" dataKey="x" name="stature" hide />
                                                <YAxis type="number" dataKey="y" name="weight" hide />
                                                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                                                <Scatter name="Telemetry" data={mockScatterData} fill="var(--accent-primary)">
                                                    {mockScatterData.map((_, index) => (
                                                        <Cell key={`cell-${index}`} fill={index % 10 === 0 ? 'var(--accent-danger)' : 'var(--accent-primary)'} />
                                                    ))}
                                                </Scatter>
                                            </ScatterChart>
                                        </ResponsiveContainer>
                                    </div>
                                ) : (
                                    <div className="detail-chart-container">
                                        <span className="mini-box-label">Package Distribution</span>
                                        <ResponsiveContainer width="100%" height="90%">
                                            <BarChart data={mockTimeSeries.slice(0, 8)}>
                                                <Bar dataKey="value" fill="var(--bg-hover)" />
                                                <Bar dataKey="anomalous" fill="var(--accent-danger)" />
                                                <Tooltip />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                )}

                                {/* Metric KPI Grid */}
                                <div className="category-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                    <div className="mini-data-box">
                                        <span className="mini-box-label">Integrity Status</span>
                                        <span className="mini-box-value" style={{ color: 'var(--accent-success)' }}>SECURED</span>
                                    </div>
                                    <div className="mini-data-box">
                                        <span className="mini-box-label">Data Sync Frequency</span>
                                        <span className="mini-box-value">250ms</span>
                                    </div>
                                    <div className="mini-data-box">
                                        <span className="mini-box-label">Encryption Protocol</span>
                                        <span className="mini-box-value">TLS 1.3</span>
                                    </div>
                                    <div className="mini-data-box">
                                        <span className="mini-box-label">Hardware Hash</span>
                                        <span className="mini-box-value" style={{ fontSize: '0.8rem' }}>0x8A4BD...2F</span>
                                    </div>
                                </div>
                            </div>

                            <div className="slide-footer">
                                <button className="btn-primary" style={{ width: '100%', justifyContent: 'center', background: 'var(--accent-primary)', color: '#000' }}>
                                    DOWNLOAD INCIDENT REPORT (CSV)
                                </button>
                            </div>
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}

export default DashboardNew;
