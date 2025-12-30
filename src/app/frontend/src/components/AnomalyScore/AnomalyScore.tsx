import { Bot, Clock, TrendingUp, Brain, BarChart3 } from 'lucide-react';
import './AnomalyScore.css';

interface AnomalyScoreProps {
    score: number;
    attackType: string;
    confidence: 'low' | 'medium' | 'high';
    lastUpdate: string;
}

export function AnomalyScore({ score, attackType, confidence, lastUpdate }: AnomalyScoreProps) {
    const getScoreColor = (score: number) => {
        if (score < 30) return '#10b981';
        if (score < 60) return '#eab308';
        if (score < 80) return '#f97316';
        return '#ef4444';
    };

    const circumference = 2 * Math.PI * 45;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
        <div className="anomaly-score">
            <div className="score-header">
                <div className="ai-badge">
                    <Bot size={14} />
                    <span>AI-POWERED</span>
                </div>
                <div className="last-update">
                    <Clock size={12} />
                    <span>{lastUpdate}</span>
                </div>
            </div>

            <div className="score-display">
                <svg className="score-ring" viewBox="0 0 100 100">
                    <circle
                        className="score-ring-bg"
                        cx="50"
                        cy="50"
                        r="45"
                        fill="none"
                        stroke="#21262d"
                        strokeWidth="8"
                    />
                    <circle
                        className="score-ring-fill"
                        cx="50"
                        cy="50"
                        r="45"
                        fill="none"
                        stroke={getScoreColor(score)}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        transform="rotate(-90 50 50)"
                    />
                </svg>
                <div className="score-value">
                    <span className="score-number" style={{ color: getScoreColor(score) }}>
                        {score}
                    </span>
                    <span className="score-percent">%</span>
                </div>
            </div>

            <div className="score-details">
                <div className="attack-prediction">
                    <TrendingUp size={14} className="prediction-icon" />
                    <span className="prediction-value">{attackType}</span>
                </div>
                <div className={`confidence-badge ${confidence}`}>
                    <Brain size={12} />
                    {confidence.toUpperCase()} CONFIDENCE
                </div>
            </div>

            <div className="score-breakdown">
                <div className="breakdown-header">
                    <BarChart3 size={14} />
                    <span>Analysis Breakdown</span>
                </div>
                <div className="breakdown-items">
                    <div className="breakdown-item">
                        <span className="breakdown-label">Behavioral</span>
                        <div className="breakdown-bar">
                            <div className="breakdown-fill" style={{ width: '75%', background: '#3b82f6' }} />
                        </div>
                        <span className="breakdown-value">75%</span>
                    </div>
                    <div className="breakdown-item">
                        <span className="breakdown-label">Protocol</span>
                        <div className="breakdown-bar">
                            <div className="breakdown-fill" style={{ width: '60%', background: '#8b5cf6' }} />
                        </div>
                        <span className="breakdown-value">60%</span>
                    </div>
                    <div className="breakdown-item">
                        <span className="breakdown-label">Temporal</span>
                        <div className="breakdown-bar">
                            <div className="breakdown-fill" style={{ width: '45%', background: '#22d3ee' }} />
                        </div>
                        <span className="breakdown-value">45%</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AnomalyScore;
