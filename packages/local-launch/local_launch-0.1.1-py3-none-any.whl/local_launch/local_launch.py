import os
import sys
import toml
from menu import main_menu, kafka_menu, exit_menu
from config_actions import interactive_config
from banner import display_banner
from kafka_runner import KafkaDeployer, start_zookeeper_and_server, stop_zookeeper_and_server
from deployer import MicroserviceDeployer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich import print
import questionary

console = Console()

def main():
    os.system("cls")
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.toml")
    config = interactive_config(config_path)

    # Setup microservice environment
    ms_deployer = MicroserviceDeployer(config)
    ms_deployer.setup_environment()

    # Kafka setup if enabled
    kafka_enabled = config.get('features', {}).get('kafka', True)
    
    kafka_runner = None
    if kafka_enabled:
        kafka_yaml = config['features']['kafka_setup_yaml']
        kafka_runner = KafkaDeployer(kafka_yaml, config['modifiable']['project_root_dir'])
    
    while True:
        action = main_menu()
        if action == "Kafka Actions":
            if kafka_enabled and kafka_runner:
                kafka_runner.menu()
            else:
                print("[yellow]Kafka feature is not enabled in config.")
        elif action == "Change Project Root Directory and Setup":
            new_dir = questionary.path("Enter new project root directory:").ask()
            config['modifiable']['project_root_dir'] = new_dir
            with open(config_path, "w") as f:
                toml.dump(config, f)
            ms_deployer.setup_environment()
        elif action == "Change Context to Kind Cluster":
            os.system(f"kubectl config use-context kind-{config['microservice']['cluster_name']}")
            print(f"[green]Switched context to kind-{config['microservice']['cluster_name']}")
        elif action == "Exit Tool":
            exit_action = exit_menu()
            if exit_action == "Exit Tool Without Deleting Cluster":
                if kafka_enabled:
                    stop_zookeeper_and_server()
                print("[bold green]Goodbye!")
                sys.exit(0)
            elif exit_action == "Exit With Deleting Cluster":
                if kafka_enabled:
                    stop_zookeeper_and_server()
                os.system(f"kind delete cluster --name {config['microservice']['cluster_name']}")
                print("[bold red]Cluster deleted. Goodbye!")
                sys.exit(0)
            elif exit_action == "Back to Main Menu":
                continue

if __name__ == "__main__":
    main()