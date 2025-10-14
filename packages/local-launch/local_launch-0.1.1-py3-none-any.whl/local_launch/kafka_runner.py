from command_runner import run_command, run_command_for_30seconds_and_return_output, run_command_background
import os
import yaml
import time
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from menu import kafka_menu
from questionary import Separator, prompt, text, path
import tempfile
import subprocess
import sys
import json
from rich.console import Console

kafka_compose_file = os.path.join(os.path.dirname(__file__), "config", "kafka-compose.yaml")

# zookeeper_process = None
# kafka_process = None

# def start_zookeeper_and_server(directory_path):
#     """Start Zookeeper and Kafka server, wait for them to be ready."""
#     global zookeeper_process, kafka_process
#     print("Navigating to the Kafka directory and starting Zookeeper and Kafka server")
#     os.chdir(directory_path)
#     # Start Zookeeper
#     zookeeper_process = run_command_background(r"bin\windows\zookeeper-server-start.bat config\zookeeper.properties")
    
#     print("Waiting for Zookeeper to start...")
#     time.sleep(20)  

#     # Start Kafka server
#     kafka_process = run_command_background(
#         r"bin\windows\kafka-server-start.bat config\server.properties",
#     )
    
#     print("Waiting for Kafka server to start...")
#     time.sleep(20)  

# def stop_zookeeper_and_server(directory_path):
#     """Stop Zookeeper and Kafka server using stop scripts."""
#     global zookeeper_process, kafka_process
#     print("Stopping Kafka server and Zookeeper...")

#     kafka_stop_script = os.path.join(directory_path, "bin", "windows", "kafka-server-stop.bat")
#     zookeeper_stop_script = os.path.join(directory_path, "bin", "windows", "zookeeper-server-stop.bat")

#     if kafka_process:
#         print("Running Kafka stop script...")
#         run_command(fr'"{kafka_stop_script}"')
#         kafka_process.terminate()
#         kafka_process.wait()
#         kafka_process = None

#     if zookeeper_process:
#         print("Running Zookeeper stop script...")
#         run_command(fr'"{zookeeper_stop_script}"')
#         zookeeper_process.terminate()
#         zookeeper_process.wait()
#         zookeeper_process = None

def start_zookeeper_and_server():
    """Start Zookeeper and Kafka server using Docker Compose from config folder."""
    print(f"Starting Zookeeper and Kafka server using Docker Compose at {kafka_compose_file}...")
    subprocess.run(["docker-compose", "-f", kafka_compose_file, "up", "-d"], check=True)
    print("Waiting for Zookeeper and Kafka to start...")
    time.sleep(20)  # Wait for containers to be ready

def stop_zookeeper_and_server():
    """Stop Zookeeper and Kafka server using Docker Compose from config folder."""
    print(f"Stopping Zookeeper and Kafka server using Docker Compose at {kafka_compose_file}...")
    subprocess.run(["docker-compose", "-f", kafka_compose_file, "down"], check=True)


# def create_kafka_topic(directory_path, topic):
#     """Create a Kafka topic."""
#     print(f"Creating Kafka topic '{topic}'")
#     bat_path = os.path.join(directory_path, "bin", "windows", "kafka-topics.bat")
#     if not os.path.exists(bat_path):
#         print(f"[red]Kafka topics script not found: {bat_path}")
#         return
#     run_command(
#         fr'"{bat_path}" --create --topic {topic} --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1'
#     )

def create_kafka_topic(topic):
    """Create a Kafka topic using Kafka CLI in Docker."""
    print(f"Creating Kafka topic '{topic}'")
    cmd = [
        "docker", "exec", "config-kafka-1",
        "kafka-topics",
        "--create",
        "--topic", topic,
        "--bootstrap-server", "localhost:29092",
        "--partitions", "1",
        "--replication-factor", "1"
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"[green]Topic '{topic}' created.")
    except subprocess.CalledProcessError as e:
        print(f"[red]Failed to create topic: {e}")

def delete_topic(topic):
    """Delete a Kafka topic using Kafka CLI in Docker."""
    print(f"Deleting Kafka topic '{topic}'")
    cmd = [
        "docker", "exec", "config-kafka-1",
        "kafka-topics",
        "--delete",
        "--topic", topic,
        "--bootstrap-server", "localhost:29092"
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"[green]Topic '{topic}' deleted.")
    except subprocess.CalledProcessError as e:
        print(f"[red]Failed to delete topic: {e}")

def delivery_report(err, msg):
    """Delivery report callback called once for each message produced."""
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def start_kafka_producer(topic, message):
    """Start Kafka producer to send a message to a topic."""
    print(f"Starting Kafka producer to send message '{message}' to topic '{topic}'")

    # Configure the producer
    conf = {
        'bootstrap.servers': 'localhost:29092',
    }

    producer = Producer(conf)

    # Produce messages
    producer.produce(topic, value=message, callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery report
    producer.flush()




def start_kafka_consumer(topic):
    """Start Kafka consumer to listen to a topic. Auto stop after 10 seconds."""
    print(f"Starting Kafka consumer to listen to topic '{topic}'")

    conf = {
        'bootstrap.servers': 'localhost:29092',
        'group.id': 'test-group',
        'auto.offset.reset': 'earliest',
    }

    consumer = Consumer(conf)
    consumer.subscribe([topic])

    start_time = time.time()
    output = []
    try:
        while True:
            if time.time() - start_time > 10:
                print("Stopping consumer after 10 seconds.")
                break
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                key = msg.key().decode() if msg.key() else None
                value = msg.value().decode() if msg.value() else None
                print(f"Key: {key}, Value: {value}")
                print(f"Partition: {msg.partition()}, Offset: {msg.offset()}")
                output.append({'key': key, 'value': value, 'partition': msg.partition(), 'offset': msg.offset()})
    finally:
        consumer.close()
    return output

def get_topic_and_message_from_yml(yaml_file_path):
    """Extract topic name and message from the YAML file."""
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    kafka_config = config.get('kafka', {})
    topic = kafka_config.get('topic', 'default-topic')
    message = kafka_config.get('message', '')
    print(f"Extracted topic: {topic}, message: {message} from {yaml_file_path}")
    return [topic, message]

# def delete_topic(directory_path, topic):
#     """Delete a Kafka topic if it exists."""
#     bat_path = os.path.join(directory_path, "bin", "windows", "kafka-topics.bat")
#     if not os.path.exists(bat_path):
#         print(f"[red]Kafka topics script not found: {bat_path}")
#         return
#     topics_output = run_command(
#         fr'"{bat_path}" --list --zookeeper localhost:2181'
#     )
#     topics = topics_output.splitlines()
#     if topic in topics:
#         run_command(
#             fr'"{bat_path}" --delete --topic {topic} --zookeeper localhost:2181'
#         )
#         print(f"Topic '{topic}' deleted.")
#     else:
#         print(f"Topic '{topic}' does not exist.")

def produce_message_menu():
    questions = [
        {
            'type': 'list',
            'name': 'kafka_produce_action',
            'message': 'How do you want to produce a message?',
            'choices': [
                'Produce Message from File',
                'Produce Message from Command Line',
                Separator(),
                'Back to Kafka Menu'
            ]
        }
    ]
    answers = prompt(questions)
    return answers['kafka_produce_action']


class KafkaDeployer:
    def __init__(self, yaml_file_path, project_root):
        self.yaml_file_path = yaml_file_path
        self.project_root = project_root
        self.topic = None
        self.message = None

    def menu(self):
        while True:
            action = kafka_menu()
            self.topic, self.message = get_topic_and_message_from_yml(self.yaml_file_path)
            if action == "Create Topic":
                create_kafka_topic(self.topic)
                print(f"[green]Topic '{self.topic}' created.")
            elif action == "Delete Topic":
                delete_topic(self.topic)
            elif action == "Produce Message":
                produce_action = produce_message_menu()
                if produce_action == "Produce Message from Command Line":
                    Console.print(f"[cyan]Current default message:[/cyan] {json.dumps(self.message, indent=2) if self.message else ''}")
                    msg = text(
                        "Enter the message as JSON (or leave blank to use the default):",
                        default=json.dumps(self.message, indent=2) if self.message else ""
                    ).ask()

                    msg = (msg or "").strip()
                    if not msg:
                        print("[red]No message provided. Exiting.")
                        return

                    try:
                        json.loads(msg)
                    except Exception as e:
                        print(f"[red]Invalid JSON: {e}")
                        return

                elif produce_action == "Produce Message from File":
                    file_path = path(
                        "Enter the path to your kafka sample message file:",
                        default = os.path.join(self.project_root, "kube", "local_launch", "sample_message.json")
                    ).ask()
                    if not os.path.exists(file_path):
                        print(f"[red]Sample message file not found: {file_path}")
                        return
                    with open(file_path, "r") as f:
                        try:
                            msg_json = json.load(f)
                            msg = json.dumps(msg_json)
                        except Exception as e:
                            print(f"[red]Failed to load JSON from file: {e}")
                            return

                else:
                    print("[red]Unknown produce action.")
                    return

                start_kafka_producer(self.topic, msg)
                print("[green]Message produced successfully.")

                # temp_path = None
                # try:
                    # Write the initial message to a temp file and close it
                    # with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tf:
                    #     tf.write(json.dumps(self.message or {}, indent=2) if isinstance(self.message, dict) else (self.message or ""))
                    #     tf.flush()
                    #     temp_path = tf.name

                    # # Open the temp file in Notepad (or nano)
                    # print("Opening notepad")
                    # notepad_cmd = ["notepad.exe", temp_path] if sys.platform.startswith("win") else ["nano", temp_path]
                    # subprocess.run(notepad_cmd)
                    # print("Exiting editor")

                    # # Read the edited content
                    # with open(temp_path, "r") as tf:
                    #     msg = tf.read().strip()

                # finally:
                #     if temp_path and os.path.exists(temp_path):
                #         os.unlink(temp_path)
            elif action == "Consume Message":
                output = start_kafka_consumer(self.topic)
                print(f"[cyan]Consumer output: {output}")
            elif action == "Back to Main Menu":
                break
