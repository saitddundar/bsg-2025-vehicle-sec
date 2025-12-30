import { Terminal, Copy } from 'lucide-react';
import './LogViewer.css';

interface LogViewerProps {
    logs: string[];
    isRunning: boolean;
}

const MOCK_LOGS = [
    "[14:02:11] INITIALIZING ISO-15118 HANDSHAKE",
    "[14:02:12] SDP REQUEST BROADCAST SENT",
    "[14:02:12] SECC RESPONSE RECEIVED: ADDR=0xFE80::1",
    "[14:02:13] SUPPORTED APP PROTOCOL SENT",
    "[14:02:13] SESSION SETUP INITIATED",
    "[14:02:14] WARNING: UNEXPECTED SEQUENCE TIMEOUT",
    "[14:02:15] MONITORING ACTIVE - BUFFER POOLING..."
];

export function LogViewer({ isRunning }: LogViewerProps) {
    return (
        <div className="console-card glass-card">
            <div className="card-header">
                <div className="header-title">
                    <Terminal size={14} />
                    <span className="card-label">System Console</span>
                </div>
                <button className="icon-btn-small"><Copy size={12} /></button>
            </div>

            <div className="console-output">
                {isRunning ? (
                    MOCK_LOGS.map((log, i) => (
                        <div key={i} className="log-line">
                            <span className="line-num">{i + 1}</span>
                            <span className={`line-text ${log.includes('WARNING') ? 'warn' : ''}`}>{log}</span>
                        </div>
                    ))
                ) : (
                    <div className="empty-state">Awaiting process initiation...</div>
                )}
            </div>
        </div>
    );
}

export default LogViewer;
