import { useEffect, useRef, useState } from 'react';
import './LogViewer.css';

interface LogViewerProps {
    logs: string[];
    isRunning: boolean;
}

export function LogViewer({ logs, isRunning }: LogViewerProps) {
    const logContainerRef = useRef<HTMLDivElement>(null);
    const [autoScroll, setAutoScroll] = useState(true);

    useEffect(() => {
        if (autoScroll && logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs, autoScroll]);

    const getLogClass = (log: string): string => {
        if (log.includes('[ERROR]') || log.includes('error')) return 'log-error';
        if (log.includes('[WARNING]') || log.includes('[!]')) return 'log-warning';
        if (log.includes('[OK]') || log.includes('[SUCCESS]')) return 'log-success';
        if (log.includes('[ATTACK]') || log.includes('[!!!]')) return 'log-attack';
        return 'log-info';
    };

    return (
        <div className="log-viewer">
            <div className="log-viewer-header">
                <h3>Console Output</h3>
                <div className="log-viewer-controls">
                    {isRunning && <span className="running-indicator">● Running</span>}
                    <label className="auto-scroll-toggle">
                        <input
                            type="checkbox"
                            checked={autoScroll}
                            onChange={(e) => setAutoScroll(e.target.checked)}
                        />
                        Auto-scroll
                    </label>
                    <span className="log-count">{logs.length} lines</span>
                </div>
            </div>
            <div className="log-container" ref={logContainerRef}>
                {logs.length === 0 ? (
                    <div className="log-empty">
                        No logs yet. Run a simulation to see output here.
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <div key={index} className={`log-line ${getLogClass(log)}`}>
                            <span className="log-line-number">{index + 1}</span>
                            <span className="log-line-content">{log}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default LogViewer;
