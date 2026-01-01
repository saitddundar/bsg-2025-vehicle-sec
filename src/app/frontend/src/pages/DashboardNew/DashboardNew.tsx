import { useState, useEffect } from 'react';
import { Activity, Shield, Zap, Clock, AlertTriangle, CheckCircle, BarChart3 } from 'lucide-react';
import './DashboardNew.css';

interface LogEntry {
    id: string;
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'critical';
    message: string;
}

type TabType = 'runcontrol' | 'status' | 'logs' | 'analytics';

export function DashboardNew() {
    const [activeTab, setActiveTab] = useState<TabType>('runcontrol');
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

    // Tabs with Run Control in center as primary button
    const leftTabs = [
        { id: 'status' as TabType, label: 'Status' },
        { id: 'logs' as TabType, label: 'Logs' },
    ];

    const rightTabs = [
        { id: 'analytics' as TabType, label: 'Analytics' },
    ];

    return (
        <div className="dashboard-new">
            {/* Tab Navigation - Run Control in Center */}
            <nav className="dashboard-tabs">
                {/* Left tabs */}
                {leftTabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}

                {/* Run Control - Center Primary Button */}
                <button
                    className={`tab-btn run-control ${activeTab === 'runcontrol' ? 'active' : ''}`}
                    onClick={() => setActiveTab('runcontrol')}
                >
                    Control
                </button>

                {/* Right tabs */}
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
                {/* RUN CONTROL TAB */}
                {activeTab === 'runcontrol' && (
                    <div className="runcontrol-tab">
                        <section className="panel full-height">
                            <header className="panel-header">
                                <h2>Control</h2>
                            </header>
                            <div className="panel-content runcontrol-placeholder">
                                <p>Control panel content will be added here</p>
                            </div>
                        </section>
                    </div>
                )}

                {/* STATUS TAB */}
                {activeTab === 'status' && (
                    <div className="status-tab">
                        {/* Status Cards */}
                        <section className="status-grid">
                            <div className="status-card status-normal">
                                <div className="status-icon"><Activity size={20} /></div>
                                <div className="status-content">
                                    <span className="status-label">System Status</span>
                                    <span className="status-value">Online</span>
                                </div>
                            </div>
                            <div className="status-card status-normal">
                                <div className="status-icon"><Shield size={20} /></div>
                                <div className="status-content">
                                    <span className="status-label">Active Threats</span>
                                    <span className="status-value">0</span>
                                </div>
                            </div>
                            <div className="status-card status-normal">
                                <div className="status-icon"><Zap size={20} /></div>
                                <div className="status-content">
                                    <span className="status-label">Active Sessions</span>
                                    <span className="status-value">3</span>
                                </div>
                            </div>
                            <div className="status-card status-normal">
                                <div className="status-icon"><Clock size={20} /></div>
                                <div className="status-content">
                                    <span className="status-label">Uptime</span>
                                    <span className="status-value">99.9%</span>
                                </div>
                            </div>
                        </section>

                        {/* General Status Panel */}
                        <section className="panel">
                            <header className="panel-header">
                                <h2>General Status</h2>
                            </header>
                            <div className="panel-content">
                                <div className="general-status">
                                    <div className="status-row">
                                        <span className="row-label">API Connection</span>
                                        <span className="row-value connected">Connected</span>
                                    </div>
                                    <div className="status-row">
                                        <span className="row-label">Database</span>
                                        <span className="row-value connected">Online</span>
                                    </div>
                                    <div className="status-row">
                                        <span className="row-label">Last Sync</span>
                                        <span className="row-value">Just now</span>
                                    </div>
                                    <div className="status-row">
                                        <span className="row-label">Active Simulations</span>
                                        <span className="row-value">0</span>
                                    </div>
                                </div>
                            </div>
                        </section>
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

            {/* Components Section */}
            <section className="components-section">
                <header className="section-header">
                    <h2>Components</h2>
                </header>
                <div className="components-grid">
                    <div className="component-placeholder">
                        <span>Component 1</span>
                    </div>
                    <div className="component-placeholder">
                        <span>Component 2</span>
                    </div>
                    <div className="component-placeholder">
                        <span>Component 3</span>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default DashboardNew;
