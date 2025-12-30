import {
    Battery,
    Plug,
    Gauge,
    Thermometer,
    Wifi,
    WifiOff,
    Zap,
    Power,
} from 'lucide-react';
import './VehicleInfo.css';

interface VehicleData {
    brand: string;
    model: string;
    year: number;
    batteryCapacity: number;
    currentSoC: number;
    chargingStatus: 'idle' | 'charging' | 'discharging' | 'error';
    connectorType: string;
    maxChargePower: number;
}

interface VehicleInfoProps {
    vehicle: VehicleData | null;
    isConnected: boolean;
}

const defaultVehicle: VehicleData = {
    brand: 'Tesla',
    model: 'Model 3',
    year: 2024,
    batteryCapacity: 75,
    currentSoC: 78,
    chargingStatus: 'idle',
    connectorType: 'CCS2',
    maxChargePower: 250,
};

export function VehicleInfo({ vehicle = defaultVehicle, isConnected = true }: VehicleInfoProps) {
    const data = vehicle || defaultVehicle;

    const statusConfig = {
        idle: { color: '#6b7280', label: 'Idle', icon: Power },
        charging: { color: '#10b981', label: 'Charging', icon: Zap },
        discharging: { color: '#3b82f6', label: 'V2G Active', icon: Battery },
        error: { color: '#ef4444', label: 'Error', icon: Power },
    };

    const status = statusConfig[data.chargingStatus];
    const StatusIcon = status.icon;
    const ConnectionIcon = isConnected ? Wifi : WifiOff;

    return (
        <div className="vehicle-info">
            <div className="vehicle-info-header">
                <span className="info-title">VEHICLE STATUS</span>
                <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                    <ConnectionIcon size={14} />
                    <span>{isConnected ? 'Connected' : 'Offline'}</span>
                </div>
            </div>

            <div className="vehicle-identity">
                <div className="vehicle-badge">
                    <span className="brand">{data.brand}</span>
                    <span className="model">{data.model}</span>
                </div>
                <span className="vehicle-year">{data.year}</span>
            </div>

            <div className="battery-section">
                <div className="battery-header">
                    <Battery size={16} className="battery-icon" />
                    <span className="battery-label">Battery</span>
                    <span className="battery-value">{data.currentSoC}%</span>
                </div>
                <div className="battery-bar">
                    <div
                        className="battery-fill"
                        style={{
                            width: `${data.currentSoC}%`,
                            background: data.currentSoC > 50 ? '#10b981' : data.currentSoC > 20 ? '#eab308' : '#ef4444'
                        }}
                    />
                </div>
                <div className="battery-capacity">{data.batteryCapacity} kWh Total</div>
            </div>

            <div className="vehicle-stats">
                <div className="stat-row">
                    <div className="stat-icon">
                        <Gauge size={14} />
                    </div>
                    <span className="stat-label">Max Power</span>
                    <span className="stat-value">{data.maxChargePower} kW</span>
                </div>

                <div className="stat-row">
                    <div className="stat-icon">
                        <Plug size={14} />
                    </div>
                    <span className="stat-label">Connector</span>
                    <span className="stat-value">{data.connectorType}</span>
                </div>

                <div className="stat-row">
                    <div className="stat-icon" style={{ color: status.color }}>
                        <StatusIcon size={14} />
                    </div>
                    <span className="stat-label">Status</span>
                    <span className="stat-value" style={{ color: status.color }}>
                        {status.label}
                    </span>
                </div>
            </div>
        </div>
    );
}

export default VehicleInfo;
