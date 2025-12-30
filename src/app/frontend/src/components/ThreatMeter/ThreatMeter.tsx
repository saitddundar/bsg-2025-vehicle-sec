import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, Siren, Activity } from 'lucide-react';
import './ThreatMeter.css';

export type ThreatLevel = 'low' | 'medium' | 'high' | 'critical';

interface ThreatMeterProps {
    level: ThreatLevel;
    anomalyCount: number;
    currentThreat?: string;
}

const threatConfig = {
    low: { value: 15, color: '#10b981', label: 'LOW', bgGlow: 'rgba(16, 185, 129, 0.15)' },
    medium: { value: 45, color: '#eab308', label: 'MEDIUM', bgGlow: 'rgba(234, 179, 8, 0.15)' },
    high: { value: 75, color: '#f97316', label: 'HIGH', bgGlow: 'rgba(249, 115, 22, 0.2)' },
    critical: { value: 95, color: '#ef4444', label: 'CRITICAL', bgGlow: 'rgba(239, 68, 68, 0.25)' },
};

export function ThreatMeter({ level, anomalyCount, currentThreat }: ThreatMeterProps) {
    const [animatedValue, setAnimatedValue] = useState(0);
    const config = threatConfig[level];

    useEffect(() => {
        const timer = setTimeout(() => {
            setAnimatedValue(config.value);
        }, 100);
        return () => clearTimeout(timer);
    }, [config.value]);

    const ThreatIcon = level === 'critical' ? Siren :
        level === 'high' ? AlertTriangle :
            level === 'medium' ? Activity : Shield;

    return (
        <div
            className="threat-meter"
            style={{ '--glow-color': config.bgGlow } as React.CSSProperties}
        >
            <div className="threat-meter-header">
                <div className="threat-icon-wrapper" style={{ color: config.color }}>
                    <ThreatIcon size={20} />
                </div>
                <span className="threat-title">THREAT LEVEL</span>
                <div className="anomaly-badge">
                    <span className="anomaly-count">{anomalyCount}</span>
                    <span className="anomaly-label">anomalies</span>
                </div>
            </div>

            <div className="threat-bar-container">
                <div className="threat-bar-bg">
                    <div
                        className="threat-bar-fill"
                        style={{
                            width: `${animatedValue}%`,
                            background: `linear-gradient(90deg, #10b981 0%, #eab308 40%, #f97316 70%, #ef4444 100%)`,
                        }}
                    />
                    <div
                        className="threat-bar-indicator"
                        style={{ left: `${animatedValue}%` }}
                    />
                </div>
                <div className="threat-bar-labels">
                    <span>LOW</span>
                    <span>MEDIUM</span>
                    <span>HIGH</span>
                    <span>CRITICAL</span>
                </div>
            </div>

            <div className="threat-status">
                <span
                    className="threat-level-badge"
                    style={{
                        backgroundColor: `${config.color}20`,
                        color: config.color,
                        borderColor: config.color,
                    }}
                >
                    {config.label}
                </span>
                {currentThreat && (
                    <span className="current-threat">
                        <Activity size={14} />
                        Active: {currentThreat}
                    </span>
                )}
            </div>
        </div>
    );
}

export default ThreatMeter;
