# EV-SEC — Vehicle & EV Charging Security Research Toolkit

BSG (Computer Systems Security) course project focusing on automotive cybersecurity. This repository contains hands-on simulations and attack/defense scenarios for:

- **EV charging infrastructure security**, with emphasis on **OCPP (1.6J / 2.0.1)** threat modeling and protocol abuse.
- **In-vehicle network security**, including **CAN-Bus**-oriented simulations (e.g., replay/DoS-like behaviors).
- Practical lab-oriented components (e.g., virtual/simulated environments) to support demonstrations and experimentation.

> **Educational / research use only.** Do not run offensive scenarios against real vehicles, EVSE devices, or production networks without explicit authorization.

---

## Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Simulation & Attack Scenarios](#simulation--attack-scenarios)
- [Getting Started](#getting-started)
- [Repository Layout](#repository-layout)
- [Safety & Legal Notice](#safety--legal-notice)
- [License](#license)

---

## Key Features

- Modular simulations for **OCPP** and **vehicle-side** behaviors
- Focus on realistic security narratives: spoofing, MitM, manipulation, DoS/PDoS patterns, and covert channels
- Designed for:
  - classroom demos
  - security experimentation in isolated labs
  - protocol understanding and threat analysis

---

## Tech Stack

| Category | Tools / Technologies |
|---|---|
| Language | Python (primary) |
| Protocols | OCPP 1.6J, OCPP 2.0.1 (scenario-driven) |
| Networking / Analysis | Scapy, Wireshark / TShark |
| Runtime / Environment | Docker, Docker Compose (where applicable) |

---

## Simulation & Attack Scenarios

The following scenarios are included as part of the project’s research and demonstration scope:

| # | Scenario | Core Idea | Example Impact |
|---:|---|---|---|
| 1 | Charging Station Identity Spoofing | Weak identity / handshake assumptions enable impersonation | Unauthorized session start, data exposure |
| 2 | In‑Motion Charging Inconsistency | Desync between EV and CSMS during dynamic charging | Incorrect SoC, safety risks, hardware stress |
| 3 | V2G Protocol Manipulation (Microgrid Destabilization) | Manipulate energy transfer/control signals | Local grid instability / unsafe load shifts |
| 4 | Stealth Beaconing (Covert C2 via Heartbeats) | Abuse legitimate messages for data exfiltration | IDS evasion, covert signaling |
| 5 | “Copycat” ECU (Replay-like behavior) | Replay valid CAN frames to mimic ECU behavior | Bypass interlocks / confuse state machines |
| 6 | HMI / Screen Manipulation | Inject malicious `DataTransfer` payloads | Phishing via UI, fraudulent payment prompts |
| 7 | Phantom SoC / MeterValues Fraud | Forge telemetry / meter data | Billing fraud, battery degradation incentives |
| 8 | Station Spoofing & DoS | Intercept boot/registration flows | Service disruption, station lockout |
| 9 | Malicious Permanent DoS (PDoS) | Firmware update abuse to “brick” devices | Permanent service outage, costly recovery |

> Notes:
> - Some scenarios may be implemented as separate simulations under `src/simulations/`.
> - Scenario naming can differ slightly per module (see module READMEs).

---

## Getting Started

### Prerequisites
- Python 3.10+ recommended
- Optional: Docker / Docker Compose (depending on the module you run)

### Installation

```bash
git clone https://github.com/saitddundar/bsg-2025-vehicle-sec.git
cd bsg-2025-vehicle-sec
pip install -r requirements.txt
```

### Running a Simulation

This repository contains multiple simulations; check the relevant module README under `src/simulations/` for exact commands.

Example (placeholder pattern):
```bash
python simulator.py --scenario "V2G_Manipulation" --target <CSMS_IP>
```

---

## Repository Layout

| Path | Description |
|---|---|
| `README.md` | Project overview (this file) |
| `docs/` | Documentation and reports (if provided) |
| `smart-swot/` | Course/project artifacts (if applicable) |
| `src/` | Source code and simulations |
| `src/simulations/` | Independent simulation modules (each may include its own README) |

---

## Safety & Legal Notice

This project is intended for **education and authorized security research** only.

- Do **not** test on real EVSE, vehicles, or networks you do not own/control.
- Use only in **isolated lab environments** (VMs, containers, test networks).
- You are responsible for complying with applicable laws and institutional policies.

---

## License

BSG 2025 Vehicle Security Project (course project).  
If you plan to reuse or redistribute, consider adding a standard license (MIT/Apache-2.0/GPL-3.0) and crediting contributors accordingly.
