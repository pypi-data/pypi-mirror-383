import os
from command_runner import run_command

def build_docker_image(docker_image, dockerfile_path):
    """Build the Docker image."""
    print(f"Building Docker image '{docker_image}' from Dockerfile at '{dockerfile_path}'...")
    dockerfile_path = os.path.abspath(dockerfile_path)
    run_command(f"docker build -t {docker_image} -f {dockerfile_path} .")

def load_image_to_kind(docker_image, cluster_name):
    """Load the Docker image to Kind."""
    print("Loading image to Kind...")
    run_command(f"kind load docker-image {docker_image} --name {cluster_name}")