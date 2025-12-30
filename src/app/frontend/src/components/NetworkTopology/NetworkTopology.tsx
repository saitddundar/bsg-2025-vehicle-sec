import { useState } from 'react';
import { Car, Zap, Cloud, User, Lock, Unlock, AlertTriangle } from 'lucide-react';
import './NetworkTopology.css';

type NodeStatus = 'normal' | 'warning' | 'attack' | 'offline';
type ConnectionStatus = 'secure' | 'compromised' | 'intercepted';

interface NetworkTopologyProps {
    vehicleStatus: NodeStatus;
    evseStatus: NodeStatus;
    csmsStatus: NodeStatus;
    connectionStatus: ConnectionStatus;
    attackerPresent: boolean;
    attackType?: string;
}

export function NetworkTopology({
    vehicleStatus = 'normal',
    evseStatus = 'normal',
    csmsStatus = 'normal',
    connectionStatus = 'secure',
    attackerPresent = false,
    attackType,
}: NetworkTopologyProps) {
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);

    const getStatusColor = (status: NodeStatus) => {
        switch (status) {
            case 'normal': return '#10b981';
            case 'warning': return '#eab308';
            case 'attack': return '#ef4444';
            case 'offline': return '#6b7280';
        }
    };

    const getConnectionColor = (status: ConnectionStatus) => {
        switch (status) {
            case 'secure': return '#22d3ee';
            case 'compromised': return '#f97316';
            case 'intercepted': return '#ef4444';
        }
    };

    const ConnectionIcon = connectionStatus === 'secure' ? Lock : Unlock;

    return (
        <div className="network-topology">
            <div className="topology-header">
                <span className="topology-title">LIVE NETWORK TOPOLOGY</span>
                <div className={`connection-badge ${connectionStatus}`}>
                    <ConnectionIcon size={12} />
                    <span>{connectionStatus.toUpperCase()}</span>
                </div>
            </div>

            <div className="topology-diagram">
                {/* Vehicle Node */}
                <div
                    className={`topology-node vehicle ${vehicleStatus}`}
                    onMouseEnter={() => setHoveredNode('vehicle')}
                    onMouseLeave={() => setHoveredNode(null)}
                >
                    <div className="node-icon-wrapper" style={{ color: getStatusColor(vehicleStatus) }}>
                        <Car size={28} />
                    </div>
                    <div className="node-label">EV</div>
                    <div
                        className="node-status-ring"
                        style={{ borderColor: getStatusColor(vehicleStatus) }}
                    />
                    {hoveredNode === 'vehicle' && (
                        <div className="node-tooltip">Electric Vehicle</div>
                    )}
                </div>

                {/* Connection Line 1 */}
                <div className="connection-line">
                    <svg viewBox="0 0 100 20" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="lineGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor={getConnectionColor(connectionStatus)} />
                                <stop offset="100%" stopColor={getConnectionColor(connectionStatus)} />
                            </linearGradient>
                        </defs>
                        <line
                            x1="0" y1="10" x2="100" y2="10"
                            stroke="url(#lineGradient1)"
                            strokeWidth="2"
                            strokeDasharray={connectionStatus !== 'secure' ? '6,3' : 'none'}
                            className="animated-line"
                        />
                    </svg>
                    <div className="data-packet" style={{ backgroundColor: getConnectionColor(connectionStatus) }} />
                </div>

                {/* EVSE Node */}
                <div
                    className={`topology-node evse ${evseStatus}`}
                    onMouseEnter={() => setHoveredNode('evse')}
                    onMouseLeave={() => setHoveredNode(null)}
                >
                    <div className="node-icon-wrapper" style={{ color: getStatusColor(evseStatus) }}>
                        <Zap size={28} />
                    </div>
                    <div className="node-label">EVSE</div>
                    <div
                        className="node-status-ring"
                        style={{ borderColor: getStatusColor(evseStatus) }}
                    />
                    {hoveredNode === 'evse' && (
                        <div className="node-tooltip">Charging Station</div>
                    )}
                </div>

                {/* Attacker Node */}
                {attackerPresent && (
                    <div className="attacker-node">
                        <div className="attacker-icon-wrapper">
                            <User size={20} />
                        </div>
                        <div className="attacker-label">ATTACKER</div>
                        {attackType && <div className="attack-type">{attackType}</div>}
                        <div className="attacker-pulse" />
                    </div>
                )}

                {/* Connection Line 2 */}
                <div className="connection-line">
                    <svg viewBox="0 0 100 20" preserveAspectRatio="none">
                        <line
                            x1="0" y1="10" x2="100" y2="10"
                            stroke={getConnectionColor(connectionStatus)}
                            strokeWidth="2"
                            strokeDasharray={connectionStatus !== 'secure' ? '6,3' : 'none'}
                            className="animated-line"
                        />
                    </svg>
                    <div className="data-packet reverse" style={{ backgroundColor: getConnectionColor(connectionStatus) }} />
                </div>

                {/* CSMS Node */}
                <div
                    className={`topology-node csms ${csmsStatus}`}
                    onMouseEnter={() => setHoveredNode('csms')}
                    onMouseLeave={() => setHoveredNode(null)}
                >
                    <div className="node-icon-wrapper" style={{ color: getStatusColor(csmsStatus) }}>
                        <Cloud size={28} />
                    </div>
                    <div className="node-label">CSMS</div>
                    <div
                        className="node-status-ring"
                        style={{ borderColor: getStatusColor(csmsStatus) }}
                    />
                    {hoveredNode === 'csms' && (
                        <div className="node-tooltip">Cloud Management</div>
                    )}
                </div>
            </div>

            <div className="topology-legend">
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#10b981' }} />
                    <span>Normal</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#eab308' }} />
                    <span>Warning</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#ef4444' }} />
                    <span>Attack</span>
                </div>
            </div>
        </div>
    );
}

export default NetworkTopology;
