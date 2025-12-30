import { AlertCircle } from 'lucide-react';
import './BottomBar.css';

interface BottomBarProps {
    events: any[];
}

export function BottomBar({ events }: BottomBarProps) {
    return (
        <footer className="app-bottom-bar">
            <div className="bar-header">
                <AlertCircle size={14} />
                <span className="bar-title">OPERATIONAL EVENT FEED</span>
            </div>
            <div className="event-stream">
                {events.length > 0 ? (
                    events.map(event => (
                        <div key={event.id} className={`event-card ${event.severity}`}>
                            <span className="event-time">{event.time}</span>
                            <span className="event-message">{event.message}</span>
                        </div>
                    ))
                ) : (
                    <div className="empty-feed">Standby. No active incidents recorded.</div>
                )}
            </div>
        </footer>
    );
}

export default BottomBar;
