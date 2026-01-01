import { Shield, Zap, Radio, Database, Cpu } from 'lucide-react';
import './Scenarios.css';

interface Scenario {
    id: string;
    title: string;
    titleJp: string;
    description: string;
    icon: React.ComponentType<{ size?: number }>;
    severity: 'critical' | 'high' | 'medium';
    author: string;
}

const scenarios: Scenario[] = [
    {
        id: 'v2g-manipulation',
        title: 'V2G Protocol Manipulation',
        titleJp: 'V2Gプロトコル操作',
        description: 'Microgrid destabilization through manipulated Vehicle-to-Grid power flow commands. Targets ISO 15118 protocol vulnerabilities to cause grid frequency fluctuations.',
        icon: Zap,
        severity: 'critical',
        author: 'Sait Dundar'
    },
    {
        id: 'phantom-soc',
        title: 'Phantom SoC Report',
        titleJp: '容量詐称攻撃',
        description: 'Fake battery capacity reporting to manipulate charging schedules and grid load balancing. EVs report false State of Charge values to gain priority.',
        icon: Database,
        severity: 'high',
        author: 'Research Team'
    },
    {
        id: 'firmware-dos',
        title: 'Firmware P-DoS Attack',
        titleJp: 'ファームウェア攻撃',
        description: 'Persistent Denial of Service through malicious firmware injection into in-vehicle networks. Bricks charging capability permanently.',
        icon: Cpu,
        severity: 'critical',
        author: 'BSG Research'
    },
    {
        id: 'ocpp-beaconing',
        title: 'OCPP Stealth Beaconing',
        titleJp: 'OCPPビーコニング',
        description: 'Covert command & control channel established through OCPP protocol messages. Uses charging status updates to exfiltrate data.',
        icon: Radio,
        severity: 'high',
        author: 'BSG Research'
    },
    {
        id: 'digital-twin',
        title: 'Digital Twin Spoofing',
        titleJp: 'デジタルツイン偽装',
        description: 'Station impersonation using cloned digital identity. Intercepts charging sessions and manipulates billing/authentication.',
        icon: Shield,
        severity: 'medium',
        author: 'BSG Research'
    }
];

export function Scenarios() {
    return (
        <div className="scenarios-page">
            <header className="scenarios-header">
                <h1>Attack Scenarios</h1>
                <p className="subtitle">EV Charging Infrastructure Threat Landscape</p>
            </header>

            <div className="scenarios-grid">
                {scenarios.map(scenario => (
                    <article key={scenario.id} className={`scenario-card severity-${scenario.severity}`}>
                        <div className="card-icon">
                            <scenario.icon size={24} />
                        </div>
                        <div className="card-content">
                            <div className="card-titles">
                                <h3>{scenario.title}</h3>
                                <span className="title-jp">{scenario.titleJp}</span>
                            </div>
                            <p className="card-desc">{scenario.description}</p>
                            <div className="card-meta">
                                <span className={`severity-badge ${scenario.severity}`}>
                                    {scenario.severity.toUpperCase()}
                                </span>
                                <span className="author">{scenario.author}</span>
                            </div>
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}

export default Scenarios;
