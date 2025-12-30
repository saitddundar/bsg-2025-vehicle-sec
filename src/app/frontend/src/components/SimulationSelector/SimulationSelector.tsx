import { useState } from 'react';
import {
    Zap,
    Wifi,
    Shield,
    AlertTriangle,
    Server,
    Radio,
    Play,
    Square,
    ChevronDown,
    Check,
} from 'lucide-react';
import type { Simulation } from '../../types';
import './SimulationSelector.css';

interface SimulationSelectorProps {
    simulations: Simulation[];
    activeSimulation: string | null;
    onSelect: (simulation: Simulation) => void;
    onStop: () => void;
}

const simulationIcons: Record<string, React.ReactNode> = {
    'sait-simulation': <Zap size={18} />,
    'erdem-simulasyon': <Wifi size={18} />,
    'sevval-simulasyon': <Shield size={18} />,
    'betul-simulasyon': <AlertTriangle size={18} />,
    'furkan-simulasyon': <Radio size={18} />,
    'default': <Server size={18} />,
};

export function SimulationSelector({
    simulations,
    activeSimulation,
    onSelect,
    onStop,
}: SimulationSelectorProps) {
    const [isOpen, setIsOpen] = useState(false);

    const activeSim = simulations.find(s => s.id === activeSimulation);

    const handleSelect = (sim: Simulation) => {
        onSelect(sim);
        setIsOpen(false);
    };

    return (
        <div className="simulation-selector">
            <div className="selector-label">SIMULATION</div>

            <div className="selector-container">
                <button
                    className={`selector-trigger ${isOpen ? 'open' : ''}`}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    <div className="trigger-content">
                        {activeSim ? (
                            <>
                                <span className="trigger-icon active">
                                    {simulationIcons[activeSim.id] || simulationIcons['default']}
                                </span>
                                <span className="trigger-text">{activeSim.name}</span>
                                <span className="trigger-status running">Running</span>
                            </>
                        ) : (
                            <>
                                <span className="trigger-icon">
                                    <Server size={18} />
                                </span>
                                <span className="trigger-text placeholder">Select Simulation</span>
                            </>
                        )}
                    </div>
                    <ChevronDown
                        size={16}
                        className={`trigger-chevron ${isOpen ? 'rotated' : ''}`}
                    />
                </button>

                {isOpen && (
                    <div className="selector-dropdown">
                        {simulations.map((sim) => (
                            <button
                                key={sim.id}
                                className={`dropdown-item ${activeSimulation === sim.id ? 'active' : ''}`}
                                onClick={() => handleSelect(sim)}
                            >
                                <span className="item-icon">
                                    {simulationIcons[sim.id] || simulationIcons['default']}
                                </span>
                                <div className="item-content">
                                    <span className="item-name">{sim.name}</span>
                                    <span className="item-description">{sim.description}</span>
                                </div>
                                {activeSimulation === sim.id && (
                                    <Check size={16} className="item-check" />
                                )}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {activeSimulation && (
                <div className="selector-controls">
                    <button className="control-btn stop" onClick={onStop}>
                        <Square size={14} />
                        <span>Stop</span>
                    </button>
                </div>
            )}

            {!activeSimulation && (
                <div className="selector-hint">
                    Select a simulation to begin threat analysis
                </div>
            )}
        </div>
    );
}

export default SimulationSelector;
