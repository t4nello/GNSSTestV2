from flask import Flask
from router import Router
from flask_sock import Sock
from data_processor import DataProcessor
from mqtt_manager import MqttManager
from session_config_manager import SessionConfigManager
from measurand_calculator import MeasurandCalculator
from algorithm import Algorithm
import json
import os

class Main:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_dependencies()
        self.setup_data_processor()
        algorithm_instance = Algorithm()
        self.sock = Sock(self.app)
        self.router = Router(app=self.app, mqtt_manager=self.mqtt_manager, config_manager=self.config_manager, data_processor=self.data_processor, measurand_calculator=MeasurandCalculator, threshold_callback=algorithm_instance.on_threshold_received)

    def setup_dependencies(self):
        self.mqtt_manager = MqttManager(self.app)
        self.config_manager = SessionConfigManager("sesison_config.json")

    def setup_data_processor(self):
        config_path = os.path.expanduser("/home/rpi4/GNSSTestV2/PythonCode/gnssTest/config.json")
        with open(config_path, "r") as f:
            config = json.load(f)
        connection_string = " ".join([f"{key}={value}" for key, value in config["database"].items()])
        self.data_processor = DataProcessor(connection_string)


if __name__ == '__main__':
    main_app = Main()

    main_app.app.run(debug=True)
