import os
import threading
import paho.mqtt.client as mqtt
from flask import Flask
from data_api import PostgresDBManager
from gps_metric_handler import GpsMetricHandler
from config_manager import ConfigManager
from session_manager import SessionManager
from algorithm import Algorithm
from router import Router
from measurands_api import MeasurandApi
import json

def mqtt_loop(config):
    mqtt_handler = mqtt.Client(config["mqtt"]["client_name"])
    config_manager = ConfigManager("session_data.json")
    session_manager = SessionManager(mqtt_handler, config_manager)
    algorithm_instance = Algorithm(mqtt_handler, session_manager)
    gps_handler = GpsMetricHandler(mqtt_handler, config_manager, session_manager, algorithm_instance)

    mqtt_handler.on_connect = gps_handler.on_connect
    mqtt_handler.on_message = gps_handler.on_message

    mqtt_handler.connect(config["mqtt"]["host"], config["mqtt"]["port"])
    mqtt_handler.loop_forever()

def flask_run(config):
    router = Router(PostgresDBManager(" ".join([f"{key}={value}" for key, value in config["database"].items()])), MeasurandApi)
    app = Flask(__name__)
    router.configure_routes(app)
    app.config['JSON_SORT_KEYS'] = False
    app.run(host=config["flask"]["host"], port=config["flask"]["port"])

def main():
    config_path = os.path.expanduser("~/gnsstest/config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    mqtt_thread = threading.Thread(target=mqtt_loop, args=(config,))
    flask_thread = threading.Thread(target=flask_run, args=(config,))

    mqtt_thread.start()
    flask_thread.start()

if __name__ == "__main__":
    main()
