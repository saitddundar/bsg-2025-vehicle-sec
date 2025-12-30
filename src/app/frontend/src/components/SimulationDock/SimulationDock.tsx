import type { Simulation } from '../../types';
import './SimulationDock.css';

interface SimulationDockProps {
    simulations: Simulation[];
    activeSimulation: string | null;
    onSelect: (simulation: Simulation) => void;
}

const simulationIcons: Record<string, string> = {
    'sait-simulation': '⚡',
    'erdem-simulasyon': '🔌',
    'sevval-simulasyon': '🔐',
    'betul-simulasyon': '🛡️',
    'furkan-simulasyon': '📡',
    'goksu-simulasyon': '🔋',
    'kardelen-simulasyon': '🚗',
    'mervan-simulasyon': '📊',
};

export function SimulationDock({ simulations, activeSimulation, onSelect }: SimulationDockProps) {
    return (
        <div className="simulation-dock">
            <div className="dock-container">
                {simulations.map((sim) => (
                    <button
                        key={sim.id}
                        className={`dock-item ${activeSimulation === sim.id ? 'active' : ''} ${sim.status === 'running' ? 'running' : ''}`}
                        onClick={() => onSelect(sim)}
                        title={sim.name}
                    >
                        <span className="dock-icon">
                            {simulationIcons[sim.id] || '📦'}
                        </span>
                        <span className="dock-label">{sim.name.split(' ')[0]}</span>
                        {sim.status === 'running' && (
                            <span className="dock-running-indicator" />
                        )}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default SimulationDock;
