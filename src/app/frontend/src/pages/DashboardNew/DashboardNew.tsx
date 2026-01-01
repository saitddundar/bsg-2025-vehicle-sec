import { useState, useEffect } from 'react';
import { Activity, Shield, Zap, Clock, AlertTriangle, CheckCircle, BarChart3, Cpu, Radio, Database, Wifi, MapPin, Battery, Gauge } from 'lucide-react';
import './DashboardNew.css';

interface LogEntry {
    id: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'critical';
    message: string;
}

type TabType = 'runcontrol' | 'evcharging' | 'cyberphysical' | 'network' | 'logs' | 'analytics';

// All attack scenarios from docs
const scenarios = [
    { id: 'v2g', name: 'V2G Protocol Manipulation', author: 'Sait Dundar', severity: 'critical' },
    { id: 'phantom-soc', name: 'Phantom SoC Report (Capacity Fraud)', author: 'Kardelen Demir', severity: 'high' },
    { id: 'firmware-pdos', name: 'Malicious Firmware P-DoS Attack', author: 'Betül Altunyuva', severity: 'critical' },
    { id: 'ocpp-beaconing', name: 'OCPP Stealth Beaconing', author: 'Göksu Kayar', severity: 'high' },
    { id: 'digital-twin', name: 'Digital Twin Spoofing', author: 'Mehmet Erdem Abacı', severity: 'medium' },
    { id: 'siren-attack', name: 'Siren Attack (Grid Destabilization)', author: 'BSG Team', severity: 'critical' },
    { id: 'display-manipulation', name: 'Display Message Manipulation', author: 'BSG Team', severity: 'medium' },
    { id: 'charging-while-moving', name: 'Charging While Moving Anomaly', author: 'BSG Team', severity: 'high' },
    { id: 'ghost-ecu', name: 'Ghost ECU Injection', author: 'BSG Team', severity: 'critical' },
];

export function DashboardNew() {
    const [activeTab, setActiveTab] = useState<TabType>('runcontrol');
    const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);

    // Mock logs
    useEffect(() => {
        const mockLogs: LogEntry[] = [
            { id: '1', timestamp: formatTime(new Date()), level: 'info', message: 'Dashboard initialized' },
            { id: '2', timestamp: formatTime(new Date(Date.now() - 5000)), level: 'info', message: 'Connected to backend API' },
            { id: '3', timestamp: formatTime(new Date(Date.now() - 15000)), level: 'info', message: 'System health check passed' },
            { id: '4', timestamp: formatTime(new Date(Date.now() - 30000)), level: 'warning', message: 'High memory usage detected' },
            { id: '5', timestamp: formatTime(new Date(Date.now() - 60000)), level: 'info', message: 'Database connection established' },
        ];
        setLogs(mockLogs);
    }, []);

    function formatTime(date: Date) {
        return date.toLocaleTimeString('en-GB', { hour12: false });
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

    return (
        <div className="dashboard-new">
            {/* Tab Navigation */}
            <nav className="dashboard-tabs">
                {leftTabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}

                <button
                    className={`tab-btn run-control ${activeTab === 'runcontrol' ? 'active' : ''}`}
                    onClick={() => setActiveTab('runcontrol')}
                >
                    Control
                </button>

                {rightTabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>

            {/* Tab Content */}
            <div className="tab-content">
                {/* CONTROL TAB */}
                {activeTab === 'runcontrol' && (
                    <div className="control-tab">
                        {/* Scenario Selection */}
                        <section className="control-scenarios">
                            <header className="section-title">
                                <h2>Attack Scenarios</h2>
                                <span className="subtitle">Select a scenario to simulate</span>
                            </header>
                            <div className="scenario-list">
                                {scenarios.map(scenario => (
                                    <button
                                        key={scenario.id}
                                        className={`scenario-item ${selectedScenario === scenario.id ? 'active' : ''} severity-${scenario.severity}`}
                                        onClick={() => setSelectedScenario(scenario.id)}
                                    >
                                        <span className="scenario-name">{scenario.name}</span>
                                        <span className="scenario-author">{scenario.author}</span>
                                    </button>
                                ))}
                            </div>
                        </section>

                        {/* Metric Categories - Large Cards */}
                        <section className="control-categories">
                            <header className="section-title">
                                <h2>Monitoring Categories</h2>
                                <span className="subtitle">Click to view detailed metrics</span>
                            </header>
                            <div className="category-cards-large">
                                {/* Category 1: EV & Charging Status */}
                                <button className="category-card-large" onClick={() => setActiveTab('evcharging')}>
                                    <div className="card-header">
                                        <div className="card-icon-large ev-icon">
                                            <Zap size={32} />
                                        </div>
                                        <div className="card-title">
                                            <h3>EV & Charging Status</h3>
                                            <p>Real-time monitoring of vehicle and charging infrastructure</p>
                                        </div>
                                    </div>
                                    <div className="card-metrics-grid">
                                        <div className="metric-item"><Gauge size={16} /> Voltage & Current</div>
                                        <div className="metric-item"><Battery size={16} /> Battery SoC</div>
                                        <div className="metric-item"><Zap size={16} /> Energy (kWh)</div>
                                        <div className="metric-item"><Cpu size={16} /> CAN Commands</div>
                                        <div className="metric-item"><AlertTriangle size={16} /> SoC Anomaly</div>
                                        <div className="metric-item"><Database size={16} /> DTC Logs</div>
                                    </div>
                                </button>

                                {/* Category 2: Cyber-Physical Consistency */}
                                <button className="category-card-large" onClick={() => setActiveTab('cyberphysical')}>
                                    <div className="card-header">
                                        <div className="card-icon-large cyber-icon">
                                            <Shield size={32} />
                                        </div>
                                        <div className="card-title">
                                            <h3>Cyber-Physical Consistency</h3>
                                            <p>Cross-validation between protocol and physical data</p>
                                        </div>
                                    </div>
                                    <div className="card-metrics-grid">
                                        <div className="metric-item"><Activity size={16} /> Speed vs Charge</div>
                                        <div className="metric-item"><MapPin size={16} /> GPS vs Station ID</div>
                                        <div className="metric-item"><Zap size={16} /> VPP vs Grid</div>
                                        <div className="metric-item"><Battery size={16} /> Discharge Power</div>
                                    </div>
                                </button>

                                {/* Category 3: Network & Protocol */}
                                <button className="category-card-large" onClick={() => setActiveTab('network')}>
                                    <div className="card-header">
                                        <div className="card-icon-large network-icon">
                                            <Wifi size={32} />
                                        </div>
                                        <div className="card-title">
                                            <h3>Network & Protocol</h3>
                                            <p>CSMS level monitoring and protocol anomalies</p>
                                        </div>
                                    </div>
                                    <div className="card-metrics-grid">
                                        <div className="metric-item"><Radio size={16} /> IP Cloning</div>
                                        <div className="metric-item"><Shield size={16} /> Signature Errors</div>
                                        <div className="metric-item"><Activity size={16} /> Command Frequency</div>
                                        <div className="metric-item"><Clock size={16} /> Heartbeat Flapping</div>
                                        <div className="metric-item"><Database size={16} /> Diagnostics Size</div>
                                        <div className="metric-item"><AlertTriangle size={16} /> Access Anomalies</div>
                                    </div>
                                </button>
                            </div>
                        </section>
                    </div>
                )}

                {/* EV & CHARGING TAB */}
                {activeTab === 'evcharging' && (
                    <div className="detail-tab">
                        <header className="detail-header">
                            <div className="detail-icon ev-icon"><Zap size={28} /></div>
                            <div>
                                <h1>EV & Charging Status</h1>
                                <p>Real-time vehicle and charging infrastructure metrics</p>
                            </div>
                        </header>
                        <div className="metrics-grid">
                            <div className="metric-card">
                                <Gauge size={24} />
                                <h3>Voltage & Current</h3>
                                <p>Real-time electrical parameters of charging session</p>
                                <div className="metric-value">-- V / -- A</div>
                            </div>
                            <div className="metric-card">
                                <Battery size={24} />
                                <h3>Battery SoC</h3>
                                <p>State of Charge reported by vehicle</p>
                                <div className="metric-value">-- %</div>
                            </div>
                            <div className="metric-card">
                                <AlertTriangle size={24} />
                                <h3>SoC Anomaly Detection</h3>
                                <p>Deviation from expected SoC curve</p>
                                <div className="metric-value status-normal">Normal</div>
                            </div>
                            <div className="metric-card">
                                <Zap size={24} />
                                <h3>Energy Delivered</h3>
                                <p>Total energy transferred (MeterValues)</p>
                                <div className="metric-value">-- kWh</div>
                            </div>
                            <div className="metric-card">
                                <Cpu size={24} />
                                <h3>CAN Bus Commands</h3>
                                <p>In-vehicle network command conflicts</p>
                                <div className="metric-value status-normal">No Conflicts</div>
                            </div>
                            <div className="metric-card">
                                <Database size={24} />
                                <h3>DTC Logs</h3>
                                <p>Vehicle diagnostic trouble codes</p>
                                <div className="metric-value">0 Active</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* CYBER-PHYSICAL TAB */}
                {activeTab === 'cyberphysical' && (
                    <div className="detail-tab">
                        <header className="detail-header">
                            <div className="detail-icon cyber-icon"><Shield size={28} /></div>
                            <div>
                                <h1>Cyber-Physical Consistency</h1>
                                <p>Cross-validation between protocol and physical sensor data</p>
                            </div>
                        </header>
                        <div className="metrics-grid">
                            <div className="metric-card">
                                <Activity size={24} />
                                <h3>Speed vs Charge State</h3>
                                <p>Detect charging while vehicle is moving</p>
                                <div className="metric-value status-normal">Consistent</div>
                            </div>
                            <div className="metric-card">
                                <MapPin size={24} />
                                <h3>GPS vs Station ID</h3>
                                <p>Location validation against station registry</p>
                                <div className="metric-value status-normal">Matched</div>
                            </div>
                            <div className="metric-card">
                                <Zap size={24} />
                                <h3>VPP Capacity vs Grid</h3>
                                <p>Virtual Power Plant vs actual grid readings</p>
                                <div className="metric-value">-- MW</div>
                            </div>
                            <div className="metric-card">
                                <Battery size={24} />
                                <h3>Discharge Power Validation</h3>
                                <p>CS discharge vs EMS demand comparison</p>
                                <div className="metric-value status-normal">Normal</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* NETWORK TAB */}
                {activeTab === 'network' && (
                    <div className="detail-tab">
                        <header className="detail-header">
                            <div className="detail-icon network-icon"><Wifi size={28} /></div>
                            <div>
                                <h1>Network & Protocol</h1>
                                <p>CSMS level monitoring, protocol anomalies and authorization</p>
                            </div>
                        </header>
                        <div className="metrics-grid">
                            <div className="metric-card">
                                <Radio size={24} />
                                <h3>IP Cloning Detection</h3>
                                <p>Same ID from multiple IP addresses</p>
                                <div className="metric-value status-normal">No Clones</div>
                            </div>
                            <div className="metric-card">
                                <Shield size={24} />
                                <h3>Signature Validation</h3>
                                <p>PKI and digital signature errors</p>
                                <div className="metric-value">0 Errors</div>
                            </div>
                            <div className="metric-card">
                                <Activity size={24} />
                                <h3>Command Frequency</h3>
                                <p>Abnormal OCPP command patterns</p>
                                <div className="metric-value status-normal">Normal</div>
                            </div>
                            <div className="metric-card">
                                <Clock size={24} />
                                <h3>Heartbeat Flapping</h3>
                                <p>Inconsistent status notifications</p>
                                <div className="metric-value status-normal">Stable</div>
                            </div>
                            <div className="metric-card">
                                <Database size={24} />
                                <h3>Diagnostics Payload</h3>
                                <p>Unusual message sizes (beaconing)</p>
                                <div className="metric-value">-- bytes</div>
                            </div>
                            <div className="metric-card">
                                <AlertTriangle size={24} />
                                <h3>Access Anomalies</h3>
                                <p>Operator login from unusual locations</p>
                                <div className="metric-value status-normal">None</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* LOGS TAB */}
                {activeTab === 'logs' && (
                    <div className="logs-tab">
                        <section className="panel full-height">
                            <header className="panel-header">
                                <h2>Recent Logs</h2>
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
                                    {logs.length === 0 && (
                                        <div className="logs-empty">No logs yet</div>
                                    )}
                                </div>
                            </div>
                        </section>
                    </div>
                )}

                {/* ANALYTICS TAB */}
                {activeTab === 'analytics' && (
                    <div className="analytics-tab">
                        <section className="panel full-height">
                            <header className="panel-header">
                                <h2>Analytics</h2>
                            </header>
                            <div className="panel-content analytics-placeholder">
                                <div className="placeholder-icon">
                                    <BarChart3 size={48} />
                                </div>
                                <h3>Coming Soon</h3>
                                <p>Analytics and metrics will be displayed here</p>
                            </div>
                        </section>
                    </div>
                )}
            </div>
        </div>
    );
}

export default DashboardNew;
