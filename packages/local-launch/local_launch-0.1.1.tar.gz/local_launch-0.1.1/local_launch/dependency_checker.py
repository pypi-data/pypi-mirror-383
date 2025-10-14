import subprocess
import sys
import os

def check_system_dependencies():
    """Check if system dependencies are installed."""
    system_dependencies = {
        "docker": "docker --version",
        "kind": "kind --version",
        "kubectl": "kubectl version --client"
    }

    for tool, command in system_dependencies.items():
        try:
            subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{tool} is installed.")
        except subprocess.CalledProcessError:
            print(f"{tool} is not installed. Please install {tool} before proceeding.")
            sys.exit(1)
