import { useState, useEffect } from 'react';
import { Activity, Shield, Zap, Clock, AlertTriangle, CheckCircle, Cpu, Radio, Database, Wifi, MapPin, Battery, Gauge, Play, Pause, FileText, TrendingUp, TrendingDown } from 'lucide-react';
import './DashboardNew.css';

interface LogEntry {
    id: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'critical';
    message: string;
}

type TabType = 'runcontrol' | 'evcharging' | 'cyberphysical' | 'network' | 'logs';

// All attack scenarios
const scenarios = [
    { id: 'v2g', name: 'V2G Protocol Manipulation', author: 'Sait Dundar', severity: 'critical' },
    { id: 'phantom-soc', name: 'Phantom SoC Report', author: 'Kardelen Demir', severity: 'high' },
    { id: 'firmware-pdos', name: 'Firmware P-DoS Attack', author: 'Betül Altunyuva', severity: 'critical' },
    { id: 'ocpp-beaconing', name: 'OCPP Stealth Beaconing', author: 'Göksu Kayar', severity: 'high' },
    { id: 'digital-twin', name: 'Digital Twin Spoofing', author: 'Mehmet Erdem Abacı', severity: 'medium' },
    { id: 'siren-attack', name: 'Siren Attack', author: 'BSG Team', severity: 'critical' },
    { id: 'display-manipulation', name: 'Display Manipulation', author: 'BSG Team', severity: 'medium' },
    { id: 'charging-moving', name: 'Charging While Moving', author: 'BSG Team', severity: 'high' },
    { id: 'ghost-ecu', name: 'Ghost ECU Injection', author: 'BSG Team', severity: 'critical' },
];

// Mini sparkline component (placeholder - will be replaced with real charts)
function Sparkline({ trend, color }: { trend: 'up' | 'down' | 'stable'; color: string }) {
    return (
        <div className="sparkline" style={{ color }}>
            {trend === 'up' && <TrendingUp size={16} />}
            {trend === 'down' && <TrendingDown size={16} />}
            {trend === 'stable' && <Activity size={16} />}
        </div>
    );
}

export function DashboardNew() {
    const [activeTab, setActiveTab] = useState<TabType>('runcontrol');
    const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [runTime, setRunTime] = useState(0);
    const [logs, setLogs] = useState<LogEntry[]>([]);

    // Timer for running scenario
    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isRunning) {
            interval = setInterval(() => setRunTime(t => t + 1), 1000);
        }
        return () => clearInterval(interval);
    }, [isRunning]);

    // Mock logs
    useEffect(() => {
        const mockLogs: LogEntry[] = [
            { id: '1', timestamp: formatTime(new Date()), level: 'info', message: 'Dashboard initialized' },
            { id: '2', timestamp: formatTime(new Date(Date.now() - 5000)), level: 'info', message: 'Connected to backend API' },
            { id: '3', timestamp: formatTime(new Date(Date.now() - 15000)), level: 'warning', message: 'High memory usage detected' },
        ];
        setLogs(mockLogs);
    }, []);

    function formatTime(date: Date) {
        return date.toLocaleTimeString('en-GB', { hour12: false });
    }

    function formatRunTime(seconds: number) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    const getLevelIcon = (level: string) => {
        switch (level) {
            case 'warning': return <AlertTriangle size={14} />;
            case 'error':
            case 'critical': return <AlertTriangle size={14} />;
            default: return <CheckCircle size={14} />;
        }
    };

    // Tab groups
    const leftTabs = [
        { id: 'evcharging' as TabType, label: 'EV/Charging' },
        { id: 'cyberphysical' as TabType, label: 'Cyber-Physical' },
    ];

    const rightTabs = [
        { id: 'network' as TabType, label: 'Network' },
        { id: 'logs' as TabType, label: 'Logs' },
    ];

    const selectedScenarioData = scenarios.find(s => s.id === selectedScenario);

    return (
        <div className="dashboard-new">
            {/* Tab Navigation */}
            <nav className="dashboard-tabs">
                {leftTabs.map(tab => (
                    <button key={tab.id} className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>{tab.label}</button>
                ))}
                <button className={`tab-btn run-control ${activeTab === 'runcontrol' ? 'active' : ''}`} onClick={() => setActiveTab('runcontrol')}>Control</button>
                {rightTabs.map(tab => (
                    <button key={tab.id} className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>{tab.label}</button>
                ))}
            </nav>

            {/* Tab Content */}
            <div className="tab-content">
                {/* CONTROL TAB */}
                {activeTab === 'runcontrol' && (
                    <div className="control-layout">
                        {/* Left: Scenario List */}
                        <aside className="scenario-sidebar">
                            <header className="sidebar-header">
                                <h2>Scenarios</h2>
                                <span className="scenario-count">{scenarios.length}</span>
                            </header>
                            <div className="scenario-list">
                                {scenarios.map(scenario => (
                                    <button
                                        key={scenario.id}
                                        className={`scenario-item ${selectedScenario === scenario.id ? 'active' : ''} severity-${scenario.severity}`}
                                        onClick={() => setSelectedScenario(scenario.id)}
                                    >
                                        <div className="scenario-info">
                                            <span className="scenario-name">{scenario.name}</span>
                                            <span className="scenario-author">{scenario.author}</span>
                                        </div>
                                        <span className={`severity-dot ${scenario.severity}`}></span>
                                    </button>
                                ))}
                            </div>
                        </aside>

                        {/* Right: Main Content */}
                        <main className="control-main">
                            {/* Sticky Scenario Header */}
                            {selectedScenarioData && (
                                <header className="scenario-header">
                                    <div className="scenario-meta">
                                        <h1>{selectedScenarioData.name}</h1>
                                        <span className={`status-badge ${isRunning ? 'running' : 'paused'}`}>
                                            {isRunning ? 'Running' : 'Ready'}
                                        </span>
                                    </div>
                                    <div className="scenario-kpis">
                                        <div className="kpi">
                                            <span className="kpi-label">Threat Level</span>
                                            <span className={`kpi-value ${selectedScenarioData.severity}`}>
                                                {selectedScenarioData.severity.toUpperCase()}
                                            </span>
                                        </div>
                                        <div className="kpi">
                                            <span className="kpi-label">Runtime</span>
                                            <span className="kpi-value mono">{formatRunTime(runTime)}</span>
                                        </div>
                                        <div className="kpi">
                                            <span className="kpi-label">Alerts</span>
                                            <span className="kpi-value">0</span>
                                        </div>
                                    </div>
                                    <div className="scenario-actions">
                                        <button className={`action-btn ${isRunning ? 'pause' : 'play'}`} onClick={() => setIsRunning(!isRunning)}>
                                            {isRunning ? <><Pause size={16} /> Pause</> : <><Play size={16} /> Start</>}
                                        </button>
                                        <button className="action-btn secondary">
                                            <FileText size={16} /> Export
                                        </button>
                                    </div>
                                </header>
                            )}

                            {!selectedScenarioData && (
                                <div className="no-scenario">
                                    <Shield size={48} />
                                    <h2>Select a Scenario</h2>
                                    <p>Choose an attack scenario from the list to start simulation</p>
                                </div>
                            )}

                            {/* Category Cards */}
                            {selectedScenarioData && (
                                <div className="category-overview">
                                    {/* EV & Charging */}
                                    <article className="category-panel" onClick={() => setActiveTab('evcharging')}>
                                        <header className="category-header">
                                            <div className="category-icon ev"><Zap size={24} /></div>
                                            <div className="category-title">
                                                <h3>EV & Charging Status</h3>
                                                <p>Real-time vehicle metrics</p>
                                            </div>
                                            <div className="status-chips">
                                                <span className="chip normal">4 Normal</span>
                                                <span className="chip warning">1 Watch</span>
                                            </div>
                                        </header>
                                        <div className="tiles-preview">
                                            <div className="tile-mini"><Gauge size={14} /> 400V / 125A</div>
                                            <div className="tile-mini"><Battery size={14} /> SoC 67%</div>
                                            <div className="tile-mini"><Zap size={14} /> 28.4 kWh</div>
                                        </div>
                                    </article>

                                    {/* Cyber-Physical */}
                                    <article className="category-panel" onClick={() => setActiveTab('cyberphysical')}>
                                        <header className="category-header">
                                            <div className="category-icon cyber"><Shield size={24} /></div>
                                            <div className="category-title">
                                                <h3>Cyber-Physical</h3>
                                                <p>Protocol vs sensor validation</p>
                                            </div>
                                            <div className="status-chips">
                                                <span className="chip normal">3 Normal</span>
                                            </div>
                                        </header>
                                        <div className="tiles-preview">
                                            <div className="tile-mini"><Activity size={14} /> Speed: OK</div>
                                            <div className="tile-mini"><MapPin size={14} /> GPS: Match</div>
                                            <div className="tile-mini"><Zap size={14} /> VPP: Normal</div>
                                        </div>
                                    </article>

                                    {/* Network */}
                                    <article className="category-panel" onClick={() => setActiveTab('network')}>
                                        <header className="category-header">
                                            <div className="category-icon network"><Wifi size={24} /></div>
                                            <div className="category-title">
                                                <h3>Network & Protocol</h3>
                                                <p>CSMS monitoring</p>
                                            </div>
                                            <div className="status-chips">
                                                <span className="chip normal">5 Normal</span>
                                            </div>
                                        </header>
                                        <div className="tiles-preview">
                                            <div className="tile-mini"><Radio size={14} /> No Clones</div>
                                            <div className="tile-mini"><Shield size={14} /> PKI: OK</div>
                                            <div className="tile-mini"><Clock size={14} /> HB: Stable</div>
                                        </div>
                                    </article>
                                </div>
                            )}
                        </main>
                    </div>
                )}

                {/* EV & CHARGING TAB */}
                {activeTab === 'evcharging' && (
                    <div className="detail-page">
                        <header className="detail-header">
                            <div className="header-icon ev"><Zap size={28} /></div>
                            <div className="header-text">
                                <h1>EV & Charging Status</h1>
                                <p>Real-time vehicle and charging infrastructure metrics</p>
                            </div>
                            <div className="header-chips">
                                <span className="chip normal">4</span>
                                <span className="chip warning">1</span>
                                <span className="chip critical">0</span>
                            </div>
                        </header>
                        <div className="metrics-grid-3">
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Gauge size={20} />
                                    <span className="tile-title">Voltage & Current</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">400V / 125A</span>
                                    <Sparkline trend="stable" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Battery size={20} />
                                    <span className="tile-title">Battery SoC</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">67%</span>
                                    <div className="progress-bar"><div className="progress-fill" style={{ width: '67%' }}></div></div>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <AlertTriangle size={20} />
                                    <span className="tile-title">SoC Anomaly</span>
                                    <span className="status-dot warning"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value warning">+2.3% deviation</span>
                                    <Sparkline trend="up" color="var(--accent-warning)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Zap size={20} />
                                    <span className="tile-title">Energy Delivered</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">28.4 kWh</span>
                                    <Sparkline trend="up" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Cpu size={20} />
                                    <span className="tile-title">CAN Commands</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">No Conflicts</span>
                                    <Sparkline trend="stable" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Database size={20} />
                                    <span className="tile-title">DTC Logs</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">0 Active</span>
                                    <span className="tile-sub">Last check: 2s ago</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* CYBER-PHYSICAL TAB */}
                {activeTab === 'cyberphysical' && (
                    <div className="detail-page">
                        <header className="detail-header">
                            <div className="header-icon cyber"><Shield size={28} /></div>
                            <div className="header-text">
                                <h1>Cyber-Physical Consistency</h1>
                                <p>Cross-validation between protocol and physical data</p>
                            </div>
                            <div className="header-chips">
                                <span className="chip normal">4</span>
                                <span className="chip warning">0</span>
                                <span className="chip critical">0</span>
                            </div>
                        </header>
                        <div className="metrics-grid-3">
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Activity size={20} />
                                    <span className="tile-title">Speed vs Charge</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">Consistent</span>
                                    <span className="tile-sub">Vehicle stationary</span>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <MapPin size={20} />
                                    <span className="tile-title">GPS vs Station ID</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">Matched</span>
                                    <span className="tile-sub">Station: CS-0042</span>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Zap size={20} />
                                    <span className="tile-title">VPP vs Grid</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">2.4 MW</span>
                                    <Sparkline trend="stable" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Battery size={20} />
                                    <span className="tile-title">Discharge Power</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">Normal</span>
                                    <span className="tile-sub">EMS demand matched</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* NETWORK TAB */}
                {activeTab === 'network' && (
                    <div className="detail-page">
                        <header className="detail-header">
                            <div className="header-icon network"><Wifi size={28} /></div>
                            <div className="header-text">
                                <h1>Network & Protocol</h1>
                                <p>CSMS level monitoring and protocol anomalies</p>
                            </div>
                            <div className="header-chips">
                                <span className="chip normal">6</span>
                                <span className="chip warning">0</span>
                                <span className="chip critical">0</span>
                            </div>
                        </header>
                        <div className="metrics-grid-3">
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Radio size={20} />
                                    <span className="tile-title">IP Cloning</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">No Clones</span>
                                    <span className="tile-sub">1 active connection</span>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Shield size={20} />
                                    <span className="tile-title">PKI Validation</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">0 Errors</span>
                                    <span className="tile-sub">Cert valid: 89 days</span>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Activity size={20} />
                                    <span className="tile-title">Command Frequency</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">Normal</span>
                                    <Sparkline trend="stable" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Clock size={20} />
                                    <span className="tile-title">Heartbeat</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">Stable</span>
                                    <span className="tile-sub">30s interval</span>
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <Database size={20} />
                                    <span className="tile-title">Diagnostics Size</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">1.2 KB</span>
                                    <Sparkline trend="stable" color="var(--accent-success)" />
                                </div>
                            </div>
                            <div className="metric-tile">
                                <div className="tile-header">
                                    <AlertTriangle size={20} />
                                    <span className="tile-title">Access Anomalies</span>
                                    <span className="status-dot normal"></span>
                                </div>
                                <div className="tile-body">
                                    <span className="tile-value">None</span>
                                    <span className="tile-sub">GeoIP: matched</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* LOGS TAB */}
                {activeTab === 'logs' && (
                    <div className="logs-page">
                        <section className="panel">
                            <header className="panel-header">
                                <h2>System Logs</h2>
                                <span className="panel-badge">{logs.length}</span>
                            </header>
                            <div className="panel-content">
                                <div className="logs-list">
                                    {logs.map(log => (
                                        <div key={log.id} className={`log-item level-${log.level}`}>
                                            <span className="log-icon">{getLevelIcon(log.level)}</span>
                                            <span className="log-time">{log.timestamp}</span>
                                            <span className="log-message">{log.message}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </section>
                    </div>
                )}
            </div>
        </div>
    );
}

export default DashboardNew;
