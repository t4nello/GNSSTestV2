# main.py
import paho.mqtt.client as mqtt
from gps_metric_handler import GpsMetricHandler
from config_manager import ConfigManager
from session_manager import SessionManager
from algorithm import Algorithm

config_manager = ConfigManager("config.json")

mqtt_handler = mqtt.Client()
session_manager = SessionManager(mqtt_handler, config_manager)

algorithm_instance = Algorithm(mqtt_handler)

gps_handler = GpsMetricHandler(mqtt_handler, config_manager, session_manager, algorithm_instance)

mqtt_handler.on_connect = gps_handler.on_connect
mqtt_handler.on_message = gps_handler.on_message

mqtt_handler.connect("192.168.0.213", 1883)

mqtt_handler.loop_forever()
