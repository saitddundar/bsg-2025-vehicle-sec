"""
EV Security Demo Launcher
Automatically starts all required services for the demo
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚗⚡ EV SECURITY RESEARCH TOOLKIT - DEMO LAUNCHER")
    print("=" * 60)
    print()

def check_requirements():
    """Check if required dependencies are installed"""
    print("📋 Checking requirements...")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found! Please install Node.js")
        return False
    
    # Check Python
    try:
        version = sys.version.split()[0]
        print(f"✅ Python: {version}")
    except:
        print("❌ Python not found!")
        return False
    
    print()
    return True

def start_backend():
    """Start Flask backend API"""
    print("🔧 Starting Backend API...")
    api_dir = Path(__file__).parent / 'src' / 'app' / 'api'
    
    if not (api_dir / 'server.py').exists():
        print("⚠️  Backend server.py not found, skipping...")
        return None
    
    # Install dependencies if needed
    if (api_dir / 'requirements.txt').exists():
        print("📦 Installing backend dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 
                       str(api_dir / 'requirements.txt')])
    
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, 'server.py'],
        cwd=str(api_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    print("✅ Backend API started at http://localhost:5000")
    print()
    return process

def start_frontend():
    """Start React frontend"""
    print("🎨 Starting Frontend Dashboard...")
    frontend_dir = Path(__file__).parent / 'src' / 'app' / 'frontend'
    
    # Install dependencies if needed
    if not (frontend_dir / 'node_modules').exists():
        print("📦 Installing frontend dependencies (this may take a while)...")
        subprocess.run(['npm', 'install'], cwd=str(frontend_dir), shell=True)
    
    # Start dev server in background
    process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=str(frontend_dir),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)
    print("✅ Frontend Dashboard started at http://localhost:5173")
    print()
    return process

def main():
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("=" * 60)
        print("🎉 DEMO IS READY!")
        print("=" * 60)
        print()
        print("📊 Dashboard:  http://localhost:5173")
        print("🔌 Backend API: http://localhost:5000")
        print()
        print("Press Ctrl+C to stop all services...")
        print()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("\n👋 Demo ended. Thank you!")

if __name__ == '__main__':
    main()
