import { useRef, useEffect } from 'react';
import { Terminal, Copy } from 'lucide-react';
import './LogViewer.css';

interface LogViewerProps {
    logs: string[];
    isRunning: boolean;
}

export function LogViewer({ logs, isRunning }: LogViewerProps) {
    const outputRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (outputRef.current) {
            outputRef.current.scrollTo({
                top: outputRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, [logs]);


    return (
        <div className="console-card glass-card">
            <div className="card-header">
                <div className="header-title">
                    <Terminal size={14} />
                    <span className="card-label">System Console</span>
                </div>
                <button
                    className="icon-btn-small"
                    onClick={() => {
                        const text = logs.join('\n');
                        navigator.clipboard.writeText(text);
                    }}
                    title="Copy to clipboard"
                >
                    <Copy size={12} />
                </button>
            </div>

            <div className="console-output" ref={outputRef}>
                {logs && logs.length > 0 ? (
                    logs.map((log, i) => (
                        <div key={i} className="log-line">
                            <span className="line-num">{i + 1}</span>
                            <span className={`line-text ${log.includes('ERROR') || log.includes('CRITICAL') || log.includes('!!!') ? 'error' :
                                log.includes('WARNING') || log.includes('[!]') ? 'warn' :
                                    log.includes('[OK]') || log.includes('PHASE') ? 'success' : ''
                                }`}>{log}</span>
                        </div>
                    ))
                ) : isRunning ? (
                    <div className="empty-state">Process started. Awaiting output stream...</div>
                ) : (
                    <div className="empty-state">Awaiting process initiation...</div>
                )}
            </div>
        </div>
    );
}

export default LogViewer;
