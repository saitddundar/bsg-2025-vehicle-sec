// Simulation Types

export interface Simulation {
    id: string;
    name: string;
    description: string;
    path: string;
    author: string;
    status: SimulationStatus;
    scripts: SimulationScript[];
}

export interface SimulationScript {
    name: string;
    file: string;
    description: string;
}

export type SimulationStatus = 'idle' | 'running' | 'completed' | 'error';

export interface SimulationLog {
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'success';
    message: string;
}

export interface SimulationRunResult {
    simulationId: string;
    scriptName: string;
    status: SimulationStatus;
    logs: SimulationLog[];
    startTime: string;
    endTime?: string;
}
