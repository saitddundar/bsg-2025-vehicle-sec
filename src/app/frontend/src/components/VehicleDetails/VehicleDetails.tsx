import './VehicleDetails.css';

interface VehicleSpec {
    label: string;
    value: string;
    category: 'battery' | 'charging' | 'communication' | 'security';
}

interface VehicleDetailsProps {
    simulationId: string | null;
}

const vehicleSpecs: Record<string, VehicleSpec[]> = {
    'sait-simulation': [
        { label: 'Protocol', value: 'OCPP 1.6 / ISO 15118', category: 'communication' },
        { label: 'V2G Support', value: 'Enabled', category: 'charging' },
        { label: 'Max Discharge', value: '11 kW', category: 'charging' },
        { label: 'Grid Connection', value: 'Microgrid', category: 'charging' },
        { label: 'Battery Chemistry', value: 'Li-ion NMC', category: 'battery' },
        { label: 'Nominal Voltage', value: '400V DC', category: 'battery' },
        { label: 'C-Rate (Discharge)', value: '1C', category: 'battery' },
        { label: 'TLS Version', value: 'TLS 1.3', category: 'security' },
        { label: 'Certificate', value: 'X.509 v3', category: 'security' },
        { label: 'Attack Vector', value: 'Protocol Manipulation', category: 'security' },
    ],
    'erdem-simulasyon': [
        { label: 'Protocol', value: 'OCPP 1.6', category: 'communication' },
        { label: 'CAN Bus', value: 'CAN 2.0B', category: 'communication' },
        { label: 'Baud Rate', value: '500 kbps', category: 'communication' },
        { label: 'GPS Module', value: 'u-blox NEO-M8', category: 'communication' },
        { label: 'Battery Type', value: 'Li-ion', category: 'battery' },
        { label: 'Capacity', value: '75 kWh', category: 'battery' },
        { label: 'Anomaly Detection', value: 'Active', category: 'security' },
        { label: 'Data Fusion', value: 'OCPP + GPS + CAN', category: 'security' },
    ],
    'sevval-simulasyon': [
        { label: 'Attack Type', value: 'MITM', category: 'security' },
        { label: 'Target Protocol', value: 'OCPP WebSocket', category: 'communication' },
        { label: 'Interception', value: 'Active', category: 'security' },
        { label: 'Encryption', value: 'Bypassed (Demo)', category: 'security' },
    ],
};

const defaultSpecs: VehicleSpec[] = [
    { label: 'Select a simulation', value: 'to view details', category: 'communication' },
];

const categoryColors: Record<string, string> = {
    battery: '#10b981',
    charging: '#3b82f6',
    communication: '#8b5cf6',
    security: '#ef4444',
};

const categoryIcons: Record<string, string> = {
    battery: '🔋',
    charging: '⚡',
    communication: '📡',
    security: '🔐',
};

export function VehicleDetails({ simulationId }: VehicleDetailsProps) {
    const specs = simulationId ? vehicleSpecs[simulationId] || defaultSpecs : defaultSpecs;

    const groupedSpecs = specs.reduce((acc, spec) => {
        if (!acc[spec.category]) {
            acc[spec.category] = [];
        }
        acc[spec.category].push(spec);
        return acc;
    }, {} as Record<string, VehicleSpec[]>);

    return (
        <div className="vehicle-details">
            <div className="details-header">
                <h3>Technical Specifications</h3>
                {simulationId && (
                    <span className="simulation-tag">{simulationId}</span>
                )}
            </div>

            <div className="details-grid">
                {Object.entries(groupedSpecs).map(([category, categorySpecs]) => (
                    <div key={category} className="spec-category">
                        <div
                            className="category-header"
                            style={{ borderLeftColor: categoryColors[category] }}
                        >
                            <span className="category-icon">{categoryIcons[category]}</span>
                            <span className="category-name">{category.charAt(0).toUpperCase() + category.slice(1)}</span>
                        </div>
                        <div className="spec-list">
                            {categorySpecs.map((spec, idx) => (
                                <div key={idx} className="spec-item">
                                    <span className="spec-label">{spec.label}</span>
                                    <span className="spec-value">{spec.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default VehicleDetails;
