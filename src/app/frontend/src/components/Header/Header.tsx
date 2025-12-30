import { Cpu } from 'lucide-react';
import './Header.css';

interface HeaderProps {
    activeSimulation?: string;
    anomalyState: 'normal' | 'suspicious' | 'attack';
}

export function Header({ activeSimulation, anomalyState }: HeaderProps) {
    return (
        <header className="app-header">
            <div className="header-center">
                {activeSimulation ? (
                    <div className={`simulation-status-tag ${anomalyState}`}>
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
        </header>
    );
}

export default Header;
