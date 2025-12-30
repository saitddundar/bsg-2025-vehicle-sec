import { Shield, Clock, Activity, Zap, Battery } from 'lucide-react';
import './Header.css';

interface HeaderProps {
    activeSimulation?: string;
    anomalyState: 'normal' | 'suspicious' | 'attack';
    elapsedTime: number;
}

export function Header({ activeSimulation, anomalyState, elapsedTime }: HeaderProps) {
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <header className={`app-header-professional ${anomalyState}`}>
            <div className="header-top-row">
                <div className="header-section logo-area">
                    <div className="brand">
                        <Shield className="brand-icon" size={18} />
                        <span className="brand-name">BSG 2025</span>
                    </div>
                    <div className="session-timer">
                        <Clock size={14} />
                        <span>{formatTime(elapsedTime)}</span>
                    </div>
                </div>

                <div className="header-center">
                    <div className={`simulation-status-tag ${anomalyState}`}>
                        {activeSimulation ? (
                            <>
                                <span className="status-label">Live Analysis:</span>
                                <span className="simulation-name">{activeSimulation}</span>
                            </>
                        ) : (
                            <span>Ready for Input</span>
                        )}
                    </div>
                </div>

                <div className="header-section kpi-area">
                    <div className="kpi-chip">
                        <Zap size={12} />
                        <span className="kpi-val">11.4 kW</span>
                    </div>
                    <div className="kpi-chip">
                        <Battery size={12} />
                        <span className="kpi-val">78.2%</span>
                    </div>
                    <div className="kpi-chip">
                        <Activity size={12} />
                        <span className="kpi-val">230V</span>
                    </div>
                </div>
            </div>

            <div className={`alert-strip ${anomalyState}`}>
                <div className="alert-content">
                    {anomalyState === 'attack' ? (
                        <>ALERT: Active V2G Injection Attack Detected</>
                    ) : anomalyState === 'suspicious' ? (
                        <>WARNING: Unusual Voltage Fluctuations Detected</>
                    ) : (
                        <>SYSTEM SECURE: All protocols operating within safe margins</>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;
