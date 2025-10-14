import os
import subprocess
import sys
import random

def check_supervisor_installed():
    try:
        subprocess.run(
            ["supervisord", "-v"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[INFO] Supervisor installing...")
        subprocess.run(["sudo", "apt", "update", "-o", "Acquire::AllowInsecureRepositories=true"], check=True)
        subprocess.run(["sudo", "apt", "install", "supervisor", "-y"], check=True)

def generate_random_code():
    return random.randint(1000, 9999)

def create_supervisor_conf(command, process_code):
    current_dir = os.getcwd()
    process_name = f"process-{process_code}"
    conf_path = f"/etc/supervisor/conf.d/{process_name}.conf"

    conf_content = f"""[program:{process_name}]
directory={current_dir}
command={command}
autostart=true
autorestart=true
stderr_logfile=/var/log/{process_name}.err.log
stdout_logfile=/var/log/{process_name}.out.log
user=root
"""

    with open(f"/tmp/{process_name}.conf", "w") as f:
        f.write(conf_content)

    subprocess.run(["sudo", "mv", f"/tmp/{process_name}.conf", conf_path], check=True)

    return process_name

def start_supervisor_process(process_name):
    subprocess.run(["sudo", "supervisorctl", "reread"], check=True)
    subprocess.run(["sudo", "supervisorctl", "update"], check=True)
    print(f"\033[92m\nSupervisor Process Started Successfully!\nProcess Name: {process_name}\033[0m")

def main():
    if len(sys.argv) < 2:
        print("Usage: supervisorex <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    check_supervisor_installed()
    process_code = generate_random_code()
    process_name = create_supervisor_conf(command, process_code)
    start_supervisor_process(process_name)

if __name__ == "__main__":
    main()
