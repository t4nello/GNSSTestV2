from flask import Flask
from flask_sock import Sock
from router import Router
from data_processor import DataProcessor
from mqtt_manager import MqttManager
from session_config_manager import SessionConfigManager
from measurand_calculator import MeasurandCalculator
from algorithm import Algorithm
import json
import os


app = Flask(__name__)
sockets = Sock(app)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 10}
config_manager = SessionConfigManager("session_config.json")
config_path = os.path.expanduser("/home/rpi4/GNSSTestV2/PythonCode/gnssTest/config.json")
with open(config_path, "r") as f:
    config = json.load(f)

connection_string = " ".join([f"{key}={value}" for key, value in config["database"].items()])
data_processor = DataProcessor(connection_string)

mqtt_manager = MqttManager(app)
algorithm = Algorithm(mqtt_manager)
mqtt_manager.set_algorithm(algorithm)

router = Router(app, sockets, mqtt_manager, config_manager, data_processor, MeasurandCalculator, algorithm)
