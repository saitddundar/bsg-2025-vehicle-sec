import { Shield, Activity, Cpu, Bell } from 'lucide-react';
import './Header.css';

interface HeaderProps {
    activeSimulation?: string;
    anomalyState: 'normal' | 'suspicious' | 'attack';
}

export function Header({ activeSimulation, anomalyState }: HeaderProps) {
    return (
        <header className="app-header">
            <div className="header-left">
                <div className="logo">
                    <Shield className="logo-icon" size={20} />
                    <span className="logo-text">BSG 2025</span>
                </div>
                <div className="divider" />
                <div className="breadcrumb">
                    <span className="breadcrumb-path">Platform</span>
                    <span className="breadcrumb-separator">/</span>
                    <span className="breadcrumb-current">Dashboard</span>
                </div>
            </div>

            <div className="header-center">
                {activeSimulation ? (
                    <div className={`simulation-status-tag ${anomalyState}`}>
                        <Activity size={14} className="pulse-icon" />
                        <span className="status-label">Live Analysis:</span>
                        <span className="simulation-name">{activeSimulation}</span>
                    </div>
                ) : (
                    <div className="simulation-status-tag idle">
                        <Cpu size={14} />
                        <span>Ready for Input</span>
                    </div>
                )}
            </div>

            <div className="header-right">
                <div className="action-icons">
                    <button className="icon-btn">
                        <Bell size={18} />
                        <span className="notification-dot" />
                    </button>
                    <div className="user-avatar">AD</div>
                </div>
            </div>
        </header>
    );
}

export default Header;
