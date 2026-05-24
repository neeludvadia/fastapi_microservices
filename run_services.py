import os
import sys
import subprocess
import time
import signal

SERVICES = [
    {"name": "user_service", "dir": "user_service", "port": 5000},
    {"name": "catalog_service", "dir": "catalog_service", "port": 8000},
    {"name": "order_service", "dir": "order_service", "port": 7000},
]

processes = []

def get_python_executable(service_dir):
    # Check for virtualenv in service directory
    venv_python_win = os.path.join(service_dir, "venv", "Scripts", "python.exe")
    venv_python_unix = os.path.join(service_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python_win):
        return venv_python_win
    elif os.path.exists(venv_python_unix):
        return venv_python_unix
    
    # Fallback to system python
    return sys.executable

def start_services():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for service in SERVICES:
        service_path = os.path.join(base_dir, service["dir"])
        if not os.path.exists(service_path):
            print(f"Directory {service_path} does not exist. Skipping...")
            continue
            
        python_bin = get_python_executable(service_path)
        print(f"Starting {service['name']} using {python_bin} on port {service['port']}...")
        
        # Start uvicorn server in a subprocess
        proc = subprocess.Popen(
            [python_bin, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(service["port"])],
            cwd=service_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append((service["name"], proc))
        
        # Print outputs in non-blocking way or log them
        # For simplicity, we print that the service is running
        print(f"Launched {service['name']} (PID: {proc.pid})")
        time.sleep(1) # Give it a second before starting next one

def monitor_and_print_logs():
    import threading
    
    def log_reader(name, proc):
        for line in iter(proc.stdout.readline, ''):
            print(f"[{name}] {line.strip()}")
        proc.stdout.close()

    threads = []
    for name, proc in processes:
        t = threading.Thread(target=log_reader, args=(name, proc), daemon=True)
        t.start()
        threads.append(t)
        
    print("\nAll services started. Press Ctrl+C to stop all services.\n")
    try:
        while True:
            # Check if any process has terminated unexpectedly
            for name, proc in processes:
                ret = proc.poll()
                if ret is not None:
                    print(f"Service {name} terminated with code {ret}")
                    return
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all services...")

def terminate_services():
    for name, proc in processes:
        print(f"Terminating {name} (PID: {proc.pid})...")
        if sys.platform == "win32":
            # On Windows, taskkill is cleaner for child process trees
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.terminate()
            
    # Wait for processes to exit
    for name, proc in processes:
        proc.wait()
    print("All services stopped.")

if __name__ == "__main__":
    start_services()
    monitor_and_print_logs()
    terminate_services()
