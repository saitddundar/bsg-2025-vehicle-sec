import { CheckCircle2, Circle } from 'lucide-react';
import './AttackTimeline.css';

interface AttackTimelineProps {
    recon: boolean;
    injection: boolean;
    detection: boolean;
}

export function AttackTimeline({ recon, injection, detection }: AttackTimelineProps) {
    const steps = [
        { id: 'recon', label: 'Reconnaissance', active: recon },
        { id: 'injection', label: 'Packet Injection', active: injection },
        { id: 'detection', label: 'Detection Triggered', active: detection },
    ];

    return (
        <div className="timeline-card glass-card">
            <div className="card-header">
                <span className="card-label">Kill Chain Tracking</span>
            </div>

            <div className="timeline-steps">
                {steps.map((step, i) => (
                    <div key={step.id} className={`step-item ${step.active ? 'active' : ''}`}>
                        <div className="step-marker">
                            {step.active ? <CheckCircle2 size={16} /> : <Circle size={16} />}
                            {i < steps.length - 1 && <div className="step-connector" />}
                        </div>
                        <span className="step-label">{step.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default AttackTimeline;

