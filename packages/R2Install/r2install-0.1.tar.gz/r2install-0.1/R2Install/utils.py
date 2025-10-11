import subprocess
import os

def get_version_and_codename():
    version = None
    codename = None
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VERSION_ID="):
                    version = line.strip().split('=')[1].strip('"')
                elif line.startswith("UBUNTU_CODENAME="):
                    codename = line.strip().split('=')[1]
                elif line.startswith("VERSION_CODENAME="):
                    codename = line.strip().split('=')[1]
        return version, codename
    except Exception as e:
        print(f"Error reading OS version and codename: {e}")
        return None, None

def update():
    subprocess.run("sudo apt update", shell=True)

def upgrade():
    subprocess.run("sudo apt upgrade", shell=True)

def get_shell():
    return os.environ.get("SHELL")


def get_active_shell():
    ppid = os.getppid()  # Get parent process ID
    shell_path = None
    try:
        # Read the executable path of the parent process
        shell_path = os.readlink(f'/proc/{ppid}/exe')
    except Exception as e:
        print(f"Could not determine shell executable: {e}")
    return shell_path