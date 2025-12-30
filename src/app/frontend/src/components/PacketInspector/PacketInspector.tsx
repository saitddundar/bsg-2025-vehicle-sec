import { Search, Filter } from 'lucide-react';
import './PacketInspector.css';

interface PacketInspectorProps {
    isRunning: boolean;
    packets: any[];
}

export function PacketInspector({ isRunning }: PacketInspectorProps) {
    return (
        <div className="packet-card glass-card">
            <div className="card-header">
                <div className="header-title">
                    <Search size={14} />
                    <span className="card-label">Deep Packet Inspection</span>
                </div>
                <button className="icon-btn-small"><Filter size={12} /></button>
            </div>

            <div className="packet-list">
                {isRunning ? (
                    <div className="packet-item suspicious">
                        <div className="packet-meta">
                            <span className="p-time">14:02:44.11</span>
                            <span className="p-type">V2G_ChargeParameterDiscoveryRes</span>
                        </div>
                        <div className="p-payload">
                            <span className="p-key">EvseMaxCurrent</span>: <span className="p-val-warn">400.0A</span>
                            <span className="p-key">EvseMinCurrent</span>: <span className="p-val">0.0A</span>
                            <span className="p-key">EvseStatus</span>: <span className="p-val">Ready</span>
                        </div>
                        <div className="p-flag">ANOMALY: Value exceeds SECC limits</div>
                    </div>
                ) : (
                    <div className="empty-state">No active telemetry streams detected.</div>
                )}
            </div>
        </div>
    );
}

export default PacketInspector;
