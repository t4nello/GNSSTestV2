import os
import threading
from flask import Flask
from mqtt_manager import MqttManager
from data_processor import DataProcessor
from router import Router
from measurand_calculator import MeasurandCalculator
import json

def mqtt_loop(config):
    mqtt_manager = MqttManager(config["mqtt"]["clientId"])
    mqtt_manager.connect(config["mqtt"]["host"], config["mqtt"]["port"])
    mqtt_manager.client.on_connect = mqtt_manager.on_connect
    mqtt_manager.loop_forever()

def flask_run(config):
    router = Router(DataProcessor(" ".join([f"{key}={value}" for key, value in config["database"].items()])), MeasurandCalculator)
    app = Flask(__name__)
    router.configure_routes(app)
    app.config['JSON_SORT_KEYS'] = False
    app.run(host=config["flask"]["host"], port=config["flask"]["port"])

def main():
    config_path = os.path.expanduser("/home/rpi4/GNSSTestV2/PythonCode/gnssTest/config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    mqtt_thread = threading.Thread(target=mqtt_loop, args=(config,))
    flask_thread = threading.Thread(target=flask_run, args=(config,))

    mqtt_thread.start()
    flask_thread.start()

if __name__ == "__main__":
    main()
