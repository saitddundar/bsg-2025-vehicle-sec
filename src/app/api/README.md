# EV Security Backend API

Simple Flask-based API for EV Security Dashboard simulation control and real-time log streaming.

## Features

- ✅ RESTful API for simulation control
- ✅ WebSocket support for real-time logs
- ✅ Scenario-specific log generation
- ✅ CORS enabled for frontend integration

## Installation

```bash
cd src/app/api
pip install -r requirements.txt
```

## Running

```bash
python server.py
```

Server will start on `http://localhost:5000`

## Endpoints

### Health Check
```bash
GET /api/health
```

### Get Scenarios
```bash
GET /api/scenarios
```

### Start Simulation
```bash
POST /api/simulation/start
Content-Type: application/json

{
  "scenario_id": "v2g-mod"
}
```

### Stop Simulation
```bash
POST /api/simulation/stop
```

### Get Status
```bash
GET /api/simulation/status
```

### Get Logs
```bash
GET /api/logs
```

## WebSocket

Connect to `ws://localhost:5000/socket.io` for real-time log updates.

Events:
- `connect`: Connection established
- `log_update`: New log entry received
