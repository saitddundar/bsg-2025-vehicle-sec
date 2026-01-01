import { ShieldAlert, Zap, Target, AlertCircle } from 'lucide-react';
import './ThreatSummary.css';

interface ImpactItem {
    type: string;
    severity: 'low' | 'medium' | 'high';
}

interface ThreatSummaryProps {
    threatType: string;
    attackVector: string;
    confidence: 'low' | 'medium' | 'high';
    potentialImpact: ImpactItem[];
    isActive: boolean;
}

export function ThreatSummary({
    threatType,
    attackVector,
    confidence,
    potentialImpact,
    isActive,
}: ThreatSummaryProps) {
    return (
        <div className={`summary-card glass-card ${isActive ? 'active' : ''}`}>
            <div className="card-header">
                <span className="card-label">Intelligence Report</span>
                <div className={`intel-status ${isActive ? 'danger' : 'secure'}`}>
                    {isActive ? 'THREAT ACTIVE' : 'SYSTEM CLEAR'}
                </div>
            </div>

            <div className="summary-body">
                <div className="intel-row">
                    <Zap size={14} className="intel-icon" />
                    <div className="intel-info">
                        <span className="intel-label">Type</span>
                        <span className="intel-value">{threatType}</span>
                    </div>
                </div>

                <div className="intel-row">
                    <Target size={14} className="intel-icon" />
                    <div className="intel-info">
                        <span className="intel-label">Vector</span>
                        <span className="intel-value">{attackVector}</span>
                    </div>
                </div>

                <div className="intel-row">
                    <ShieldAlert size={14} className="intel-icon" />
                    <div className="intel-info">
                        <span className="intel-label">Prognosis</span>
                        <div className="impact-tags">
                            {potentialImpact.map((imp, i) => (
                                <span key={i} className={`impact-tag ${imp.severity}`}>
                                    {imp.type}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {isActive && (
                <div className={`confidence-footer ${confidence}`}>
                    <AlertCircle size={12} />
                    <span>Confidence: {confidence.toUpperCase()}</span>
                </div>
            )}
        </div>
    );
}

export default ThreatSummary;

