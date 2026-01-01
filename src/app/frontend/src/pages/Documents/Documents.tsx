import { Shield, Zap, Radio, Database, Cpu } from 'lucide-react';
import './Documents.css';

interface Document {
    id: string;
    title: string;
    description: string;
    details: string[];
    icon: React.ComponentType<{ size?: number }>;
    severity: 'critical' | 'high' | 'medium';
    author: string;
}

const documents: Document[] = [
    {
        id: 'v2g-manipulation',
        title: 'V2G Protocol Manipulation',
        description: 'This attack targets the Vehicle-to-Grid communication protocol (ISO 15118) to destabilize microgrids. By manipulating power flow commands between EVs and the grid, attackers can cause frequency fluctuations that may lead to blackouts.',
        details: [
            'Exploits bidirectional power flow in V2G systems',
            'Targets ISO 15118 protocol handshake vulnerabilities',
            'Can cause cascading grid failures in microgrid environments',
            'Requires compromised charging station or MITM position'
        ],
        icon: Zap,
        severity: 'critical',
        author: 'Sait Dundar'
    },
    {
        id: 'phantom-soc',
        title: 'Phantom SoC Report (Capacity Fraud)',
        description: 'Electric vehicles report false State of Charge (SoC) values to charging infrastructure. This manipulation allows attackers to game priority charging queues, steal electricity, or disrupt grid load balancing algorithms.',
        details: [
            'Falsified battery capacity reporting to CSMS',
            'Enables electricity theft through fake low-battery claims',
            'Disrupts smart charging schedule optimization',
            'Can overload grid during peak demand periods'
        ],
        icon: Database,
        severity: 'high',
        author: 'Kardelen Demir'
    },
    {
        id: 'firmware-dos',
        title: 'Malicious Firmware P-DoS Attack',
        description: 'Persistent Denial of Service attack through malicious firmware injection into vehicle charging systems. Once installed, the corrupted firmware permanently disables charging capability until hardware replacement.',
        details: [
            'Targets EVSE firmware update mechanisms',
            'Exploits insecure OTA update channels',
            'Causes permanent charging disability (requires hardware swap)',
            'Can spread through compromised update servers'
        ],
        icon: Cpu,
        severity: 'critical',
        author: 'Betül Altunyuva'
    },
    {
        id: 'ocpp-beaconing',
        title: 'OCPP Stealth Beaconing',
        description: 'Establishes a covert command & control channel using legitimate OCPP protocol messages. Attackers hide malicious commands within standard charging status updates, making detection extremely difficult.',
        details: [
            'Uses OCPP StatusNotification for C2 communication',
            'Data exfiltration through charging transaction metadata',
            'Bypasses traditional network security monitoring',
            'Persistent access through scheduled heartbeat messages'
        ],
        icon: Radio,
        severity: 'high',
        author: 'Göksu Kayar'
    },
    {
        id: 'digital-twin',
        title: 'Digital Twin Station Spoofing',
        description: 'Attackers create a cloned digital identity of legitimate charging stations. This fake "digital twin" intercepts charging sessions, manipulates billing data, and can harvest authentication credentials.',
        details: [
            'Clones station identity certificates and metadata',
            'Enables man-in-the-middle on charging sessions',
            'Billing fraud through manipulated transaction records',
            'Credential harvesting from EV authentication attempts'
        ],
        icon: Shield,
        severity: 'medium',
        author: 'Mehmet Erdem Abacı'
    }
];


export function Documents() {
    return (
        <div className="documents-page">
            <header className="documents-header">
                <h1>Documents</h1>
                <p className="subtitle">EV Charging Infrastructure - Attack Scenario Research</p>
            </header>

            <div className="documents-grid">
                {documents.map(doc => (
                    <article key={doc.id} className={`document-card severity-${doc.severity}`}>
                        <div className="card-icon">
                            <doc.icon size={24} />
                        </div>
                        <div className="card-content">
                            <h3>{doc.title}</h3>
                            <p className="card-desc">{doc.description}</p>
                            <ul className="card-details">
                                {doc.details.map((detail, i) => (
                                    <li key={i}>{detail}</li>
                                ))}
                            </ul>
                            <div className="card-meta">
                                <span className={`severity-badge ${doc.severity}`}>
                                    {doc.severity.toUpperCase()}
                                </span>
                                <span className="author">by {doc.author}</span>
                            </div>
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}

export default Documents;
