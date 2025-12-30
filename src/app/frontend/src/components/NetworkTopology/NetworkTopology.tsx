import { Car, Zap, Cloud, ShieldAlert, Lock, Unlock } from 'lucide-react';
import './NetworkTopology.css';

interface NetworkTopologyProps {
    vehicleStatus: 'normal' | 'warning' | 'attack' | 'offline';
    evseStatus: 'normal' | 'warning' | 'attack' | 'offline';
    csmsStatus: 'normal' | 'warning' | 'attack' | 'offline';
    connectionStatus: 'secure' | 'compromised' | 'intercepted';
    attackerPresent: boolean;
    flowDirection: 'charging' | 'discharging' | 'idle';
}

export function NetworkTopology({
    vehicleStatus,
    evseStatus,
    csmsStatus,
    connectionStatus,
    attackerPresent,
    flowDirection
}: NetworkTopologyProps) {
    return (
        <div className="topology-card glass-card">
            <div className="card-header">
                <span className="card-label">Network Architecture</span>
                <div className={`threat-status-badge ${connectionStatus}`}>
                    {connectionStatus === 'secure' ? <Lock size={12} /> : <ShieldAlert size={12} />}
                    <span>{connectionStatus.toUpperCase()}</span>
                </div>
            </div>

            <div className="topology-visual">
                <div className="nodes-row">
                    {/* Vehicle Node */}
                    <div className={`network-node ${vehicleStatus}`}>
                        <div className="node-icon"><Car size={24} /></div>
                        <span className="node-name">Asset EV</span>
                    </div>

                    <div className="connection-path">
                        <div className={`link-line ${flowDirection}`}>
                            {flowDirection !== 'idle' && (
                                <div className="flow-particles">
                                    <div className="dot" />
                                    <div className="dot" />
                                    <div className="dot" />
                                </div>
                            )}
                        </div>
                    </div>

                    {/* EVSE Node */}
                    <div className={`network-node ${evseStatus}`}>
                        <div className="node-icon"><Zap size={24} /></div>
                        <span className="node-name">Gateway EVSE</span>
                    </div>

                    <div className="connection-path">
                        <div className="link-line static" />
                        {attackerPresent && (
                            <div className="attack-vector-marker">
                                <ShieldAlert size={20} className="flash-icon" />
                                <div className="interference-line" />
                            </div>
                        )}
                    </div>

                    {/* Cloud Node */}
                    <div className={`network-node ${csmsStatus}`}>
                        <div className="node-icon"><Cloud size={24} /></div>
                        <span className="node-name">Cloud Backend</span>
                    </div>
                </div>
            </div>

            <div className="topology-footer">
                <div className="legend">
                    <div className="legend-item"><span className="dot normal" /> Normal</div>
                    <div className="legend-item"><span className="dot warning" /> Suspicious</div>
                    <div className="legend-item"><span className="dot attack" /> Intervention</div>
                </div>
            </div>
        </div>
    );
}

export default NetworkTopology;
