import sys
import time
import subprocess
from api.api import app

def start_services():
    # Fix stdout encoding for Windows
    sys.stdout.reconfigure(encoding='utf-8')
    print("🛡️ Starting Q-Safe AI Services...")
    
    # Start FastAPI
    print("-> Starting FastAPI Backend (Port 8000)...")
    api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.api:app", "--host", "127.0.0.1", "--port", "8000"])
    
    time.sleep(3) # Wait for backend to initialize
    
    # Start Streamlit
    print("-> Starting Streamlit Dashboard...")
    ui_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "ui/app.py"])
    
    try:
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        api_process.terminate()
        ui_process.terminate()
        print("Done.")

if __name__ == "__main__":
    start_services()
