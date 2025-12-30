import './PacketInspector.css';

interface Packet {
    id: string;
    timestamp: string;
    type: string;
    direction: 'incoming' | 'outgoing';
    protocol: string;
    payload: Record<string, unknown>;
    suspicious: boolean;
    suspiciousFields?: string[];
}

interface PacketInspectorProps {
    packets: Packet[];
    isRunning: boolean;
}

const mockPackets: Packet[] = [
    {
        id: '1',
        timestamp: '14:32:45.123',
        type: 'BootNotification',
        direction: 'incoming',
        protocol: 'OCPP 1.6',
        payload: {
            chargePointVendor: 'BSG-Energy',
            chargePointModel: 'V2G-Station-Pro',
            firmwareVersion: '1.2.3',
        },
        suspicious: false,
    },
    {
        id: '2',
        timestamp: '14:32:48.456',
        type: 'MeterValues',
        direction: 'incoming',
        protocol: 'OCPP 1.6',
        payload: {
            connectorId: 1,
            meterValue: [{
                timestamp: '2024-12-30T14:32:48Z',
                sampledValue: [{
                    value: '99999999',
                    measurand: 'Energy.Active.Export.Register',
                    unit: 'Wh',
                }],
            }],
        },
        suspicious: true,
        suspiciousFields: ['meterValue.sampledValue.value'],
    },
    {
        id: '3',
        timestamp: '14:32:50.789',
        type: 'DataTransfer',
        direction: 'outgoing',
        protocol: 'OCPP 1.6',
        payload: {
            vendorId: 'V2G-Attack',
            messageId: 'StartDischarge',
            data: { power_kw: 50, bypass_safety: true },
        },
        suspicious: true,
        suspiciousFields: ['data.bypass_safety', 'data.power_kw'],
    },
];

export function PacketInspector({ packets = mockPackets, isRunning }: PacketInspectorProps) {
    const renderValue = (value: unknown, path: string, suspiciousFields: string[] = []): JSX.Element => {
        const isSuspicious = suspiciousFields.some(f => path.includes(f) || f.includes(path));

        if (typeof value === 'object' && value !== null) {
            return (
                <div className="json-object">
                    {'{'}
                    <div className="json-content">
                        {Object.entries(value).map(([k, v], i) => (
                            <div key={k} className="json-line">
                                <span className="json-key">"{k}"</span>
                                <span className="json-colon">: </span>
                                {renderValue(v, `${path}.${k}`, suspiciousFields)}
                                {i < Object.entries(value).length - 1 && <span className="json-comma">,</span>}
                            </div>
                        ))}
                    </div>
                    {'}'}
                </div>
            );
        }

        if (Array.isArray(value)) {
            return (
                <span className="json-array">
                    [{value.map((v, i) => (
                        <span key={i}>
                            {renderValue(v, `${path}[${i}]`, suspiciousFields)}
                            {i < value.length - 1 && ', '}
                        </span>
                    ))}]
                </span>
            );
        }

        const valueClass = typeof value === 'string' ? 'json-string' :
            typeof value === 'number' ? 'json-number' :
                typeof value === 'boolean' ? 'json-boolean' : 'json-null';

        return (
            <span className={`${valueClass} ${isSuspicious ? 'suspicious' : ''}`}>
                {typeof value === 'string' ? `"${value}"` : String(value)}
            </span>
        );
    };

    return (
        <div className="packet-inspector">
            <div className="inspector-header">
                <span className="inspector-title">DEEP PACKET INSPECTION</span>
                <div className="inspector-status">
                    {isRunning && <span className="live-dot" />}
                    <span>{isRunning ? 'LIVE' : 'PAUSED'}</span>
                </div>
            </div>

            <div className="packets-container">
                {packets.map((packet) => (
                    <div
                        key={packet.id}
                        className={`packet-item ${packet.suspicious ? 'suspicious' : ''} ${packet.direction}`}
                    >
                        <div className="packet-header">
                            <div className="packet-meta">
                                <span className="packet-time">{packet.timestamp}</span>
                                <span className={`packet-direction ${packet.direction}`}>
                                    {packet.direction === 'incoming' ? '←' : '→'}
                                </span>
                                <span className="packet-type">{packet.type}</span>
                            </div>
                            <div className="packet-badges">
                                <span className="protocol-badge">{packet.protocol}</span>
                                {packet.suspicious && (
                                    <span className="suspicious-badge">⚠️ SUSPICIOUS</span>
                                )}
                            </div>
                        </div>
                        <div className="packet-payload">
                            {renderValue(packet.payload, '', packet.suspiciousFields)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default PacketInspector;
