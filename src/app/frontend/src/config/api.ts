// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiConfig = {
    baseUrl: API_BASE_URL,
    endpoints: {
        simulations: '/api/simulations',
        run: '/api/simulations/run',
        stop: '/api/simulations/stop',
        status: '/api/simulations/status',
    },
    wsUrl: API_BASE_URL.replace('http', 'ws') + '/ws',
};

export default apiConfig;
