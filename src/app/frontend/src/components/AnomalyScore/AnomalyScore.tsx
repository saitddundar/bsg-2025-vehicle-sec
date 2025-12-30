import { Bot, Binary } from 'lucide-react';
import './AnomalyScore.css';

interface AnomalyScoreProps {
    score: number;
}

export function AnomalyScore({ score }: AnomalyScoreProps) {
    const getProgressColor = () => {
        if (score < 30) return 'var(--accent-success)';
        if (score < 70) return 'var(--accent-warning)';
        return 'var(--accent-danger)';
    };

    return (
        <div className="score-card glass-card">
            <div className="card-header">
                <span className="card-label">Computational Diagnostics</span>
                <div className="ai-status">
                    <Bot size={12} />
                    <span>CORE NEURAL ENGINE</span>
                </div>
            </div>

            <div className="score-display">
                <div className="radial-wrapper">
                    <svg viewBox="0 0 100 100" className="radial-svg">
                        <circle cx="50" cy="50" r="42" className="track" />
                        <circle
                            cx="50" cy="50" r="42"
                            className="progress"
                            style={{
                                strokeDasharray: `${2 * Math.PI * 42}`,
                                strokeDashoffset: `${2 * Math.PI * 42 * (1 - score / 100)}`,
                                stroke: getProgressColor()
                            }}
                        />
                    </svg>
                    <div className="score-text">
                        <span className="score-num" style={{ color: getProgressColor() }}>{score}</span>
                        <span className="score-percent">%</span>
                    </div>
                </div>
            </div>

            <div className="score-footer">
                <Binary size={14} className="footer-icon" />
                <span>Anomaly Probability Vector Identified</span>
            </div>
        </div>
    );
}

export default AnomalyScore;
