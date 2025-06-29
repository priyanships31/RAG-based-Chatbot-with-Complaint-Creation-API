import subprocess
import sys
import time
import webbrowser
from threading import Thread
import socket
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_command(command, service_name, port=None):
    try:
        if port and is_port_in_use(port):
            print(f"⚠️ {service_name} port {port} is already in use")
            return False
        
        print(f"🚀 Starting {service_name}...")
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to start {service_name}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error starting {service_name}: {str(e)}")
        return False

if __name__ == "__main__":
    # Kill existing processes if needed (uncomment if you want this behavior)
    # os.system("pkill -f 'uvicorn main:app'")
    # os.system("pkill -f 'streamlit run app.py'")
    
    # Start FastAPI backend
    backend = Thread(
        target=run_command,
        args=("uvicorn backend_app:app --reload --port 8000", "FastAPI backend", 8000),
        daemon=True
    )
    backend.start()

    # Start Streamlit frontend
    frontend = Thread(
        target=run_command,
        args=("streamlit run frontend_app.py --server.port 8501", "Streamlit frontend", 8501),
        daemon=True
    )
    frontend.start()

    # Wait for servers to start
    time.sleep(3)

    # Open browser tabs if ports are available
    # if not is_port_in_use(8000):
    #     webbrowser.open("http://localhost:8000/docs")
    if not is_port_in_use(8501):
        webbrowser.open("http://localhost:8501")

    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Servers shutting down...")
        sys.exit(0)