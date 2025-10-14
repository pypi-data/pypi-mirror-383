import os
import sys
import toml
from dependency_checker import check_system_dependencies
from cluster_manager import is_cluster_running, create_cluster, create_namespace
from docker_manager import build_docker_image, load_image_to_kind
from command_runner import run_command
from kafka_runner import (
    start_zookeeper_and_server, stop_zookeeper_and_server,
)

from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich import print
import questionary

console = Console()

class MicroserviceDeployer:
    def __init__(self, config):
        self.banner_name = config['locallaunch']['banner_name']

        self.docker_image = config['microservice']['docker_image']
        self.dockerfile_path = config['microservice']['dockerfile_path']
        self.project_root_dir = config['modifiable']['project_root_dir']
        self.kube_kustomize_path = config['microservice']['kube_kustomize_path']
        self.namespace = config['microservice']['namespace']
        self.cluster_name = config['microservice']['cluster_name']
        self.kind_config_path = config['microservice']['kind_config_path']
        self.kafka_compose = config['microservice']['kafka_path']


    def check_dependencies(self):
        """Check and install necessary dependencies."""
        check_system_dependencies()

    def change_to_project_root(self):
        """Change the current working directory to the project base directory."""
        try:
            os.chdir(self.project_root_dir)
            console.print(f"[green]Changed directory to project base: {self.project_root_dir}")
        except Exception as e:
            raise Exception(f"Failed to change directory to {self.project_root_dir}: {str(e)}")
        
    def setup_environment(self):
        """Run the setup steps with progress bar."""
        with Progress() as progress:
            task = progress.add_task("[cyan]Setting up environment...", total=7)
            # 1. Check dependencies
            check_system_dependencies()
            progress.update(task, advance=1)
            # 2. Change to project root and switch to kind cluster
            
            os.chdir(self.project_root_dir)
            progress.update(task, advance=1)
            # 3. Cluster setup
            if not is_cluster_running(self.cluster_name):
                create_cluster(self.cluster_name, self.kind_config_path)
            progress.update(task, advance=1)
            # 4. Namespace
            create_namespace(self.namespace)
            progress.update(task, advance=1)
            # 5. Docker build
            build_docker_image(self.docker_image, self.dockerfile_path)
            progress.update(task, advance=1)
            # 6. Load image and apply kustomize
            load_image_to_kind(self.docker_image, self.cluster_name)
            #run_command(f"kubectl apply -k {self.kube_kustomize_path} --namespace {self.namespace}")
            progress.update(task, advance=1)

            #7. Setup kafka
            stop_zookeeper_and_server()
            start_zookeeper_and_server()

            console.print("[green]Kafka and Zookeeper started.\n")
            # progress.update(task, advance=1)
        console.print(Panel.fit("[bold green] Environment setup complete![/bold green]"))
