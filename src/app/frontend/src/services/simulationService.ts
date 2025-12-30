import type { Simulation, SimulationRunResult } from '../types';
import apiConfig from '../config/api';

// Fetch all simulations
export async function getSimulations(): Promise<Simulation[]> {
    const response = await fetch(`${apiConfig.baseUrl}${apiConfig.endpoints.simulations}`);
    if (!response.ok) {
        throw new Error('Failed to fetch simulations');
    }
    return response.json();
}

// Run a simulation script
export async function runSimulation(
    simulationId: string,
    scriptName: string
): Promise<SimulationRunResult> {
    const response = await fetch(`${apiConfig.baseUrl}${apiConfig.endpoints.run}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ simulationId, scriptName }),
    });
    if (!response.ok) {
        throw new Error('Failed to run simulation');
    }
    return response.json();
}

// Stop a running simulation
export async function stopSimulation(simulationId: string): Promise<void> {
    const response = await fetch(`${apiConfig.baseUrl}${apiConfig.endpoints.stop}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ simulationId }),
    });
    if (!response.ok) {
        throw new Error('Failed to stop simulation');
    }
}

// Get simulation status
export async function getSimulationStatus(simulationId: string): Promise<SimulationRunResult> {
    const response = await fetch(
        `${apiConfig.baseUrl}${apiConfig.endpoints.status}/${simulationId}`
    );
    if (!response.ok) {
        throw new Error('Failed to get simulation status');
    }
    return response.json();
}

// WebSocket connection for real-time logs
export function connectToSimulationLogs(
    simulationId: string,
    onMessage: (log: string) => void,
    onError?: (error: Event) => void
): WebSocket {
    const ws = new WebSocket(`${apiConfig.wsUrl}/logs/${simulationId}`);

    ws.onmessage = (event) => {
        onMessage(event.data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
    };

    return ws;
}
