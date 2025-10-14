from command_runner import run_command
import sys

def is_cluster_running(cluster_name):
    """Check if the Kind cluster is running."""
    try:
        run_command(f"kubectl get nodes --context kind-{cluster_name}")
        print(f"Cluster '{cluster_name}' is already running.")
        return True
    except Exception:
        print(f"Cluster '{cluster_name}' is not running.")
        return False

def create_cluster(cluster_name, kind_config_path):
    """Create a Kind cluster using the specified configuration."""
    try:
        print(f"Creating Kind cluster '{cluster_name}' using config '{kind_config_path}'...")
        run_command(f"kind create cluster --name {cluster_name} --config {kind_config_path}")
        print(f"Cluster '{cluster_name}' created successfully.")
    except Exception as e:
        print(f"Failed to create cluster '{cluster_name}': {e}")
        sys.exit(1)

def create_namespace(namespace):
    """Create a Kubernetes namespace for the microservice."""
    print(f"Creating Kubernetes namespace '{namespace}'...")
    try:
        run_command(f"kubectl create namespace {namespace}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Namespace '{namespace}' already exists. Skipping creation.")
        else:
            raise