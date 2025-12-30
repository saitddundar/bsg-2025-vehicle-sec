import { useState, useMemo } from 'react';
import './MetricsChart.css';

interface MetricsChartProps {
    isRunning: boolean;
    anomalyState: 'normal' | 'suspicious' | 'attack';
}

export function MetricsChart({ isRunning, anomalyState }: MetricsChartProps) {
    const [selectedMetric, setSelectedMetric] = useState<'voltage' | 'current' | 'temp'>('voltage');

    // Generate stable mock path
    const points = useMemo(() => {
        return Array.from({ length: 40 }, (_, i) => {
            const base = selectedMetric === 'voltage' ? 230 : selectedMetric === 'current' ? 32 : 38;
            const noise = Math.random() * 4 - 2;
            const anomaly = (anomalyState !== 'normal' && i > 25) ? (selectedMetric === 'voltage' ? 25 : 15) : 0;
            return base + noise + anomaly;
        });
    }, [selectedMetric, anomalyState, isRunning]);

    const max = Math.max(...points, 255);
    const min = Math.min(...points, 200);

    const getY = (val: number) => 150 - ((val - min) / (max - min)) * 150;
    const getX = (i: number) => (i / (points.length - 1)) * 500;

    const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p)}`).join(' ');
    const areaData = `${pathData} L 500 150 L 0 150 Z`;

    const getStrokeColor = () => {
        if (anomalyState === 'attack') return 'var(--accent-danger)';
        if (anomalyState === 'suspicious') return 'var(--accent-warning)';
        return 'var(--accent-primary)';
    };

    return (
        <div className="metrics-card glass-card">
            <div className="card-header">
                <div className="title-group">
                    <span className="card-label">Physical Telemetry</span>
                    <h3 className="card-title">Live Parameter Analysis</h3>
                </div>
                <div className="metric-switcher">
                    <button className={selectedMetric === 'voltage' ? 'active' : ''} onClick={() => setSelectedMetric('voltage')}>V</button>
                    <button className={selectedMetric === 'current' ? 'active' : ''} onClick={() => setSelectedMetric('current')}>A</button>
                    <button className={selectedMetric === 'temp' ? 'active' : ''} onClick={() => setSelectedMetric('temp')}>°C</button>
                </div>
            </div>

            <div className="chart-wrapper">
                <div className="y-axis-labels">
                    <span>{max.toFixed(0)}</span>
                    <span>{((max + min) / 2).toFixed(0)}</span>
                    <span>{min.toFixed(0)}</span>
                </div>

                <svg viewBox="0 0 500 150" className="telemetry-svg" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                            <stop offset="0%" stopColor={getStrokeColor()} stopOpacity="0.2" />
                            <stop offset="100%" stopColor={getStrokeColor()} stopOpacity="0" />
                        </linearGradient>
                    </defs>

                    {/* Grid lines */}
                    <line x1="0" y1="37" x2="500" y2="37" className="grid-line" />
                    <line x1="0" y1="75" x2="500" y2="75" className="grid-line" />
                    <line x1="0" y1="112" x2="500" y2="112" className="grid-line" />

                    {/* Area */}
                    <path d={areaData} fill="url(#chartGradient)" />

                    {/* Line */}
                    <path
                        d={pathData}
                        fill="none"
                        stroke={getStrokeColor()}
                        strokeWidth="1.5"
                        className="telemetry-path"
                    />

                    {/* Threshold line */}
                    <line
                        x1="0" y1={getY(250)} x2="500" y2={getY(250)}
                        className="threshold-marker"
                        stroke="var(--accent-danger)"
                        strokeDasharray="4,4"
                    />
                </svg>
            </div>

            <div className="metrics-footer">
                <div className="stat-pill">
                    <span className="pill-label">CURRENT</span>
                    <span className="pill-value">{points[points.length - 1].toFixed(2)}</span>
                </div>
                <div className="stat-pill">
                    <span className="pill-label">MEAN</span>
                    <span className="pill-value">{(points.reduce((a, b) => a + b) / points.length).toFixed(2)}</span>
                </div>
                <div className="stat-pill danger">
                    <span className="pill-label">DEV</span>
                    <span className="pill-value">{(points[points.length - 1] - 230).toFixed(1)}%</span>
                </div>
            </div>
        </div>
    );
}

export default MetricsChart;
