# ⚡ EV-SEC: OCPP Protocol Vulnerability & Simulation Framework 🛡️

This repository hosts a comprehensive security analysis and simulation suite for the **Open Charge Point Protocol (OCPP)**. Our research identifies critical architectural flaws in EV charging infrastructures and provides Proof-of-Concept (PoC) simulations for 9 distinct attack vectors.

---

## 🛠️ Tech Stack

* 🔌 **Protocol:** OCPP 1.6J / 2.0.1
* 🐍 **Language:** Python (Asyncio, Scapy)
* 🐳 **Environment:** Docker & Docker Compose
* 🔍 **Analysis:** Wireshark, TShark

---

## 📑 Simulation Scenarios

### 1️⃣ Charging Station Identity Spoofing 🎭

* **Threat:** Exploiting weak WebSocket handshakes to impersonate a legitimate Charge Point.
* **Impact:** Unauthorized transaction initiation and sensitive data interception.

### 2️⃣ In-Motion Charging Inconsistency 🏎️💨

* **Threat:** Manipulating synchronization between the Vehicle and CSMS during dynamic wireless charging.
* **Impact:** State-of-Charge (SoC) desynchronization and potential hardware strain.

### 3️⃣ V2G Protocol Manipulation (Microgrid Destabilization) 📉

* **Threat:** Tampering with Vehicle-to-Grid discharge commands to send false load data.
* **Severity:** 🔴 Critical - Can trigger local grid frequency instability.

### 4️⃣ Stealth Beaconing (Silent C2 Channel) 🤫

* **Threat:** Utilizing standard `Heartbeat` packets as a covert channel for data exfiltration.
* **Impact:** Bypasses traditional IDS by hiding traffic within legitimate protocol noise.

### 5️⃣ "Copycat" ECU 🤖

* **Threat:** Simulating a compromised Electronic Control Unit that replays valid CAN bus messages.
* **Impact:** Bypassing hardware safety interlocks during the high-voltage handshake.

### 6️⃣ Screen Manipulation (HMI Hijacking) 📺

* **Threat:** Injecting malicious `DataTransfer` payloads to override the station's display.
* **Impact:** Phishing via fraudulent QR codes or fake payment instructions.

### 7️⃣ Phantom SoC Report (Capacity Fraud) 🔋

* **Threat:** Forging `MeterValues` to report inaccurate battery levels to the CSMS.
* **Impact:** Financial billing fraud and intentional battery degradation.

### 8️⃣ Station Spoofing & Denial of Service (DoS) 🚫

* **Threat:** MitM attack intercepting `BootNotification` requests.
* **Impact:** Total service disruption by preventing legitimate vehicle discovery.

### 9️⃣ Malicious Permanent DoS (PDoS) 💀

* **Threat:** Exploiting the `UpdateFirmware` routine to inject corrupted binary blobs.
* **Impact:** Permanent hardware "bricking" requiring physical controller replacement.

---

## ⚙️ Installation & Usage

```bash
# Clone the repository
git clone https://github.com/saitddundar/bsg-2025-vehicle-sec/tree/main

# Install dependencies
pip install -r requirements.txt

# Execute a specific simulation
python simulator.py --scenario "V2G_Manipulation" --target <CSMS_IP>

```
