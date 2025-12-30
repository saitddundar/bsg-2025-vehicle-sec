import type { Simulation, SimulationStatus } from '../../types';
import './SimulationCard.css';

interface SimulationCardProps {
    simulation: Simulation;
    onRun: (simulation: Simulation) => void;
    onStop: (simulation: Simulation) => void;
}

const statusColors: Record<SimulationStatus, string> = {
    idle: '#6b7280',
    running: '#3b82f6',
    completed: '#10b981',
    error: '#ef4444',
};

const statusLabels: Record<SimulationStatus, string> = {
    idle: 'Idle',
    running: 'Running',
    completed: 'Completed',
    error: 'Error',
};

export function SimulationCard({ simulation, onRun, onStop }: SimulationCardProps) {
    const isRunning = simulation.status === 'running';

    return (
        <div className="simulation-card">
            <div className="simulation-card-header">
                <h3 className="simulation-card-title">{simulation.name}</h3>
                <span
                    className="simulation-card-status"
                    style={{ backgroundColor: statusColors[simulation.status] }}
                >
                    {statusLabels[simulation.status]}
                </span>
            </div>

            <p className="simulation-card-description">{simulation.description}</p>

            <div className="simulation-card-meta">
                <span className="simulation-card-author">By: {simulation.author}</span>
                <span className="simulation-card-scripts">
                    {simulation.scripts.length} script(s)
                </span>
            </div>

            <div className="simulation-card-scripts-list">
                {simulation.scripts.map((script) => (
                    <div key={script.file} className="simulation-script-item">
                        <span className="script-name">{script.name}</span>
                        <span className="script-file">{script.file}</span>
                    </div>
                ))}
            </div>

            <div className="simulation-card-actions">
                {isRunning ? (
                    <button
                        className="btn btn-stop"
                        onClick={() => onStop(simulation)}
                    >
                        Stop
                    </button>
                ) : (
                    <button
                        className="btn btn-run"
                        onClick={() => onRun(simulation)}
                    >
                        Run
                    </button>
                )}
            </div>
        </div>
    );
}

export default SimulationCard;
