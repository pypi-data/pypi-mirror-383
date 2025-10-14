import os
import questionary
import toml
from banner import display_banner 

def interactive_config(config_path):
    """Prompt user for missing config and save to TOML."""
    if not os.path.exists(config_path):
        config = {}
    else:
        config = toml.load(config_path)

    banner_name = config.get('locallaunch', {}).get('banner_name', 'locallaunch')
    display_banner(banner_name)

    # Project root dir
    project_root = config.get('modifiable', {}).get('project_root_dir')
    if not project_root or not os.path.isdir(project_root):
        project_root = questionary.path(
            "Enter your project root directory:",
            default=os.getcwd()
        ).ask()
        config.setdefault('modifiable', {})['project_root_dir'] = project_root

    microservice_name = os.path.basename(os.path.normpath(project_root))
    docker_image = f"{microservice_name}-image"

    dockerfile_path = os.path.join(project_root, "Dockerfile")
    kube_kustomize_path = os.path.join(project_root, "kube", "kustomize", "overlays", "test")

    config.setdefault('microservice', {})
    config['microservice']['docker_image'] = docker_image
    config['microservice']['dockerfile_path'] = dockerfile_path
    config['microservice']['kube_kustomize_path'] = kube_kustomize_path

    # Kafka setup
    kafka_enabled = config.get('features', {}).get('kafka', True)
    if kafka_enabled:
        kafka_yaml = config.get('features', {}).get('kafka_setup_yaml')
        if not kafka_yaml or not os.path.isfile(kafka_yaml):
            kafka_yaml = questionary.path(
                "Enter path to your Kafka setup YAML:",
                default=os.path.join(project_root, "kube", "local_launch", "local_launch.yaml")
            ).ask()
            if not kafka_yaml or not os.path.isfile(kafka_yaml):
                print(f"Skipping this test due to file not existing: {kafka_yaml}")
            else:
                config.setdefault('features', {})['kafka_setup_yaml'] = kafka_yaml
        elif not os.path.isfile(kafka_yaml):
            print(f"Skipping this test due to file not existing: {kafka_yaml}")

    # Save config
    with open(config_path, "w") as f:
        toml.dump(config, f)
    return config
