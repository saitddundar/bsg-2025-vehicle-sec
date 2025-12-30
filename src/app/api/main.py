from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import os
import subprocess
import asyncio
import json
from datetime import datetime
from pydantic import BaseModel

app = FastAPI(title="BSG 2025 Simulation API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Constants
# __file__ is src/app/api/main.py
# dirname is src/app/api
# .. is src/app
# ../.. is src
SIMULATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../simulations"))


# Known Simulation Metadata for better UI
SIM_METADATA = {
    "sait-simulation": {
        "name": "Vehicle-to-Grid (V2G) Security",
        "description": "Analysis of ISO 15118 protocol vulnerabilities and power grid stability attacks.",
        "author": "Sait Dundar"
    },
    "erdem-simulasyon": {
        "name": "Intrusion Detection System",
        "description": "Network traffic analysis and anomaly detection for EV charging infrastructure.",
        "author": "Erdem"
    },
    "mervan-simulasyon": {
        "name": "V2G Gateway Security",
        "description": "Securing the communication channel between EV and EVSE.",
        "author": "Mervan"
    },
    "furkan-simulasyon": {
        "name": "Charging Node Monitoring",
        "description": "Real-time monitoring and threat detection for charging station nodes.",
        "author": "Furkan"
    }
}

# Models
class SimulationScript(BaseModel):
    name: str
    file: str
    description: str

class Simulation(BaseModel):
    id: str
    name: str
    description: str
    path: str
    author: str
    status: str
    scripts: List[SimulationScript]

class RunRequest(BaseModel):
    simulationId: str
    scriptName: str

# In-memory storage for active processes and logs
active_processes: Dict[str, subprocess.Popen] = {}
simulation_logs: Dict[str, List[Dict]] = {}
connected_websockets: Dict[str, List[WebSocket]] = {}

def get_simulations_list():

    simulations = []
    print(f"DEBUG: Searching simulations in {SIMULATIONS_DIR}")
    if not os.path.exists(SIMULATIONS_DIR):
        print(f"DEBUG: Path {SIMULATIONS_DIR} NOT FOUND")
        return simulations
    
    for folder in os.listdir(SIMULATIONS_DIR):
        folder_path = os.path.join(SIMULATIONS_DIR, folder)
        if os.path.isdir(folder_path):
            scripts = []
            files = os.listdir(folder_path)
            # Strong priority for combined/main simulation scripts
            py_files = [f for f in files if f.endswith(".py") and not f.startswith("__")]
            
            def get_priority(filename):
                fn = filename.lower()
                # Absolute priority for combined/orchestrator scripts
                if fn == "v2g_simulation.py" or fn == "main.py": return 0
                if "combined" in fn and "simulation" in fn: return 1
                if "v2g" in fn and "simulation" in fn: return 2
                if "simulation" in fn: return 3
                if "main" in fn: return 4
                if "v2g" in fn: return 5
                return 10

            py_files.sort(key=lambda x: (get_priority(x), x.lower()))

            for file in py_files:
                scripts.append({
                    "name": file.replace(".py", "").replace("_", " ").title(),
                    "file": file,
                    "description": f"Executable: {file}"
                })


            
            # Use metadata if available, otherwise fallback
            meta = SIM_METADATA.get(folder, {
                "name": folder.replace("-", " ").title(),
                "description": f"Simulasyon ortami: {folder}",
                "author": "BSG Research"
            })

            simulations.append({
                "id": folder,
                "name": meta["name"],
                "description": meta["description"],
                "path": folder_path,
                "author": meta["author"],
                "status": "idle",
                "scripts": scripts
            })
    print(f"DEBUG: Found {len(simulations)} simulations")
    return simulations


@app.get("/api/simulations")
async def list_simulations():
    return get_simulations_list()

@app.post("/api/simulations/run")
async def run_simulation(request: RunRequest):
    sims = get_simulations_list()
    sim = next((s for s in sims if s["id"] == request.simulationId), None)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    script = next((scr for scr in sim["scripts"] if scr["name"] == request.scriptName), None)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    import sys
    script_path = os.path.join(sim["path"], script["file"])
    
    # Start process
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
            cwd=sim["path"]
        )

        active_processes[request.simulationId] = process
        simulation_logs[request.simulationId] = []
        
        # Start background task to read logs
        asyncio.create_task(read_logs(request.simulationId, process))
        
        return {
            "simulationId": request.simulationId,
            "scriptName": request.scriptName,
            "status": "running",
            "startTime": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulations/stop")
async def stop_simulation(request: Dict):
    sim_id = request.get("simulationId")
    if sim_id in active_processes:
        process = active_processes[sim_id]
        if process.poll() is None:
            process.terminate()
            return {"status": "stopped"}
    return {"status": "not_running"}

@app.get("/api/simulations/status/{simulation_id}")
async def get_status(simulation_id: str):
    if simulation_id in active_processes:
        poll = active_processes[simulation_id].poll()
        if poll is None:
            return {"status": "running"}
        return {"status": "completed" if poll == 0 else "error"}
    return {"status": "idle"}

async def read_logs(sim_id: str, process: subprocess.Popen):
    while True:
        line = await asyncio.to_thread(process.stdout.readline)
        if not line and process.poll() is not None:
            break
        if line:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": line.strip()
            }
            if "error" in line.lower() or "exception" in line.lower():
                log_entry["level"] = "error"
            elif "warning" in line.lower():
                log_entry["level"] = "warning"
            
            simulation_logs[sim_id].append(log_entry)
            
            # Broadcast to connected websockets
            if sim_id in connected_websockets:
                message = json.dumps(log_entry)
                for ws in connected_websockets[sim_id]:
                    try:
                        await ws.send_text(message)
                    except:
                        pass

@app.websocket("/ws/logs/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    await websocket.accept()
    if simulation_id not in connected_websockets:
        connected_websockets[simulation_id] = []
    connected_websockets[simulation_id].append(websocket)
    
    # Send existing logs
    if simulation_id in simulation_logs:
        for log in simulation_logs[simulation_id]:
            await websocket.send_text(json.dumps(log))
            
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        connected_websockets[simulation_id].remove(websocket)
        if not connected_websockets[simulation_id]:
            del connected_websockets[simulation_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
