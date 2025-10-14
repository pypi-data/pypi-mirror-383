import subprocess

def run_command(command):
    """Run a shell command and return the output."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {stderr.decode('utf-8')}")
    return stdout.decode('utf-8')

def run_command_background(command):
    """Run a shell command in the background."""
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_command_for_30seconds_and_return_output(command):
    """Run a shell command for 30 seconds and return the output."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            raise Exception(f"Command failed: {stderr.decode('utf-8')}")
        return stdout.decode('utf-8')
    except subprocess.TimeoutExpired:
        process.kill()
        raise Exception("Command closed after 30 seconds")