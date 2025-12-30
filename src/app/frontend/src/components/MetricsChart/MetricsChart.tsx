import { useState, useEffect } from 'react';
import './MetricsChart.css';

interface MetricData {
    voltage: number[];
    current: number[];
    temperature: number[];
    timestamps: string[];
}

interface MetricsChartProps {
    isRunning: boolean;
    hasAnomaly: boolean;
    anomalyIndex?: number;
}

const generateMockData = (hasAnomaly: boolean, anomalyIndex: number = -1): MetricData => {
    const timestamps = Array.from({ length: 20 }, (_, i) => {
        const d = new Date();
        d.setSeconds(d.getSeconds() - (20 - i) * 3);
        return d.toLocaleTimeString('en-US', { hour12: false, second: '2-digit', minute: '2-digit' });
    });

    return {
        voltage: timestamps.map((_, i) => {
            const base = 230 + Math.random() * 4 - 2;
            return hasAnomaly && i >= anomalyIndex && i < anomalyIndex + 3 ? base + 25 : base;
        }),
        current: timestamps.map((_, i) => {
            const base = 32 + Math.random() * 2 - 1;
            return hasAnomaly && i >= anomalyIndex && i < anomalyIndex + 3 ? base + 15 : base;
        }),
        temperature: timestamps.map((_, i) => {
            const base = 35 + Math.random() * 3;
            return hasAnomaly && i >= anomalyIndex && i < anomalyIndex + 3 ? base + 12 : base;
        }),
        timestamps,
    };
};

export function MetricsChart({ isRunning, hasAnomaly, anomalyIndex = 12 }: MetricsChartProps) {
    const [data, setData] = useState<MetricData>(() => generateMockData(hasAnomaly, anomalyIndex));
    const [selectedMetric, setSelectedMetric] = useState<'voltage' | 'current' | 'temperature'>('voltage');

    useEffect(() => {
        if (!isRunning) return;

        const interval = setInterval(() => {
            setData(generateMockData(hasAnomaly, anomalyIndex));
        }, 3000);

        return () => clearInterval(interval);
    }, [isRunning, hasAnomaly, anomalyIndex]);

    const metricConfig = {
        voltage: { label: 'Voltage', unit: 'V', color: '#22d3ee', threshold: 253 },
        current: { label: 'Current', unit: 'A', color: '#3b82f6', threshold: 45 },
        temperature: { label: 'Temperature', unit: '°C', color: '#f97316', threshold: 45 },
    };

    const config = metricConfig[selectedMetric];
    const values = data[selectedMetric];
    const max = Math.max(...values) * 1.1;
    const min = Math.min(...values) * 0.9;

    return (
        <div className="metrics-chart">
            <div className="chart-header">
                <span className="chart-title">PHYSICAL PARAMETERS</span>
                <div className="metric-tabs">
                    {Object.entries(metricConfig).map(([key, cfg]) => (
                        <button
                            key={key}
                            className={`metric-tab ${selectedMetric === key ? 'active' : ''}`}
                            onClick={() => setSelectedMetric(key as typeof selectedMetric)}
                            style={{ '--tab-color': cfg.color } as React.CSSProperties}
                        >
                            {cfg.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="chart-container">
                <div className="chart-y-axis">
                    <span>{max.toFixed(0)}</span>
                    <span>{((max + min) / 2).toFixed(0)}</span>
                    <span>{min.toFixed(0)}</span>
                </div>

                <div className="chart-area">
                    <svg viewBox="0 0 400 150" preserveAspectRatio="none" className="chart-svg">
                        {/* Threshold line */}
                        <line
                            x1="0"
                            y1={150 - ((config.threshold - min) / (max - min)) * 150}
                            x2="400"
                            y2={150 - ((config.threshold - min) / (max - min)) * 150}
                            stroke="#ef4444"
                            strokeWidth="1"
                            strokeDasharray="4,4"
                            opacity="0.5"
                        />

                        {/* Anomaly zone highlight */}
                        {hasAnomaly && (
                            <rect
                                x={(anomalyIndex / 20) * 400}
                                y="0"
                                width={(3 / 20) * 400}
                                height="150"
                                fill="rgba(239, 68, 68, 0.15)"
                            />
                        )}

                        {/* Line chart */}
                        <polyline
                            fill="none"
                            stroke={config.color}
                            strokeWidth="2"
                            points={values
                                .map((v, i) => {
                                    const x = (i / (values.length - 1)) * 400;
                                    const y = 150 - ((v - min) / (max - min)) * 150;
                                    return `${x},${y}`;
                                })
                                .join(' ')}
                        />

                        {/* Gradient fill */}
                        <defs>
                            <linearGradient id={`gradient-${selectedMetric}`} x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0%" stopColor={config.color} stopOpacity="0.3" />
                                <stop offset="100%" stopColor={config.color} stopOpacity="0" />
                            </linearGradient>
                        </defs>
                        <polygon
                            fill={`url(#gradient-${selectedMetric})`}
                            points={`0,150 ${values
                                .map((v, i) => {
                                    const x = (i / (values.length - 1)) * 400;
                                    const y = 150 - ((v - min) / (max - min)) * 150;
                                    return `${x},${y}`;
                                })
                                .join(' ')} 400,150`}
                        />

                        {/* Data points */}
                        {values.map((v, i) => {
                            const x = (i / (values.length - 1)) * 400;
                            const y = 150 - ((v - min) / (max - min)) * 150;
                            const isOutlier = v > config.threshold;
                            return (
                                <circle
                                    key={i}
                                    cx={x}
                                    cy={y}
                                    r={isOutlier ? 5 : 3}
                                    fill={isOutlier ? '#ef4444' : config.color}
                                    className={isOutlier ? 'outlier-point' : ''}
                                />
                            );
                        })}
                    </svg>
                </div>
            </div>

            <div className="chart-stats">
                <div className="stat-box">
                    <span className="stat-label">Current</span>
                    <span className="stat-value" style={{ color: config.color }}>
                        {values[values.length - 1].toFixed(1)} {config.unit}
                    </span>
                </div>
                <div className="stat-box">
                    <span className="stat-label">Average</span>
                    <span className="stat-value">
                        {(values.reduce((a, b) => a + b) / values.length).toFixed(1)} {config.unit}
                    </span>
                </div>
                <div className="stat-box">
                    <span className="stat-label">Threshold</span>
                    <span className="stat-value" style={{ color: '#ef4444' }}>
                        {config.threshold} {config.unit}
                    </span>
                </div>
            </div>
        </div>
    );
}

export default MetricsChart;
