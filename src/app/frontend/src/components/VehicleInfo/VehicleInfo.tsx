import { Zap, Battery, Gauge, Terminal } from 'lucide-react';
import './VehicleInfo.css';

interface VehicleInfoProps {
    vehicle: any;
    isConnected: boolean;
    soc?: number;
    power?: number;
}

export function VehicleInfo({ isConnected, soc = 78.2, power = 11.4 }: VehicleInfoProps) {
    return (
        <div className="spec-card glass-card">
            <div className="card-header">
                <span className="card-label">Asset Specifications</span>
                <div className={`connection-pill ${isConnected ? 'online' : 'offline'}`}>
                    {isConnected ? 'REMOTE LINK ACTIVE' : 'NO CONNECTION'}
                </div>
            </div>

            <div className="spec-body">
                <div className="main-spec">
                    <span className="asset-name">Tesla Model 3</span>
                    <span className="asset-tag">ID: VIN-7829-BSG</span>
                </div>

                <div className="spec-grid">
                    <div className="spec-item">
                        <Battery size={16} className="spec-icon" />
                        <div className="spec-data">
                            <span className="spec-label">SOC</span>
                            <span className="spec-value">{soc}%</span>
                        </div>
                    </div>
                    <div className="spec-item">
                        <Zap size={16} className="spec-icon" />
                        <div className="spec-data">
                            <span className="spec-label">LINE LOAD</span>
                            <span className="spec-value">{power.toFixed(1)} kW</span>
                        </div>
                    </div>
                    <div className="spec-item">
                        <Gauge size={16} className="spec-icon" />
                        <div className="spec-data">
                            <span className="spec-label">PROTO</span>
                            <span className="spec-value">ISO 15118</span>
                        </div>
                    </div>
                    <div className="spec-item">
                        <Terminal size={16} className="spec-icon" />
                        <div className="spec-data">
                            <span className="spec-label">STATUS</span>
                            <span className="spec-value">{isConnected ? (power > 0 ? 'DISCHARGING' : 'CHARGING') : 'IDLE'}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}


export default VehicleInfo;
