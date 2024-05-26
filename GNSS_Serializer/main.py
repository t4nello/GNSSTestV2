import threading
import paho.mqtt.client as mqtt
from flask import Flask
from database_manager import PostgresDBManager
from gps_metric_handler import GpsMetricHandler
from config_manager import ConfigManager
from session_manager import SessionManager
from algorithm import Algorithm
from router import Router

def mqtt_loop():
    mqtt_handler = mqtt.Client("gnssSerializer")
    config_manager = ConfigManager("config.json")
    session_manager = SessionManager(mqtt_handler, config_manager)
    algorithm_instance = Algorithm(mqtt_handler, session_manager)
    gps_handler = GpsMetricHandler(mqtt_handler, config_manager, session_manager, algorithm_instance)

    mqtt_handler.on_connect = gps_handler.on_connect
    mqtt_handler.on_message = gps_handler.on_message

    mqtt_handler.connect("localhost", 1883)
    mqtt_handler.loop_forever()

def flask_run():
    router = Router(PostgresDBManager("host=localhost user=postgres password=admin123 dbname=tsdb"))
    app = Flask(__name__)
    router.configure_routes(app)
    app.run(host='0.0.0.0', port=5000)
    app.config['JSON_SORT_KEYS'] = False

def main():
    mqtt_thread = threading.Thread(target=mqtt_loop)
    flask_thread = threading.Thread(target=flask_run)

    mqtt_thread.start()
    flask_thread.start()

if __name__ == "__main__":
    main()
