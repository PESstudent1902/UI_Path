import os
import sys
import subprocess
import webbrowser
import time
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("====================================================================")
    print("  AI-Powered Garment Tech Pack Case Management System - Launcher")
    print("====================================================================")
    print()
    
    # Get current project directory
    if getattr(sys, 'frozen', False):
        project_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Path to virtual env python
    if sys.platform == "win32":
        python_exe = os.path.join(project_dir, "venv", "Scripts", "python.exe")
    else:
        python_exe = os.path.join(project_dir, "venv", "bin", "python")
        
    if not os.path.exists(python_exe):
        print(f"[Error] Virtual environment not found at: {os.path.dirname(python_exe)}")
        print("Please run the run_portal.bat first to initialize dependencies.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    port = 8000
    server_process = None
    
    if is_port_in_use(port):
        print(f"[Info] Port {port} is already in use. Server might already be running.")
    else:
        print("[System] Starting FastAPI backend server...")
        server_path = os.path.join(project_dir, "ai-agent")
        
        # Start uvicorn using the virtual environment python
        server_process = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=server_path
        )
        time.sleep(2)
        
    print("[System] Opening dashboard in your default browser...")
    webbrowser.open(f"http://127.0.0.1:{port}/")
    
    print()
    print("Dashboard launched successfully!")
    print("Keep this window open to keep the backend server running.")
    print("Press CTRL+C or close this window to stop the server.")
    print("====================================================================")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[System] Shutting down...")
    finally:
        if server_process:
            print("[System] Stopping backend server process...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
