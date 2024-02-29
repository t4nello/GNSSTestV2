import json
import paho.mqtt.client as mqtt
import time

class GpsMetricHandler:
    def __init__(self, mqtt_client, config_manager, session_manager, algorithm):
        self.mqtt_client = mqtt_client
        self.config_manager = config_manager
        self.session_manager = session_manager
        self.algorithm = algorithm

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.mqtt_client.subscribe("gps/+")
        self.mqtt_client.subscribe("esp/connection/+")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        self.handle_message(topic)
        self.enable_algorithm(topic, message)
        self.check_connection(topic, message)
        self.session_manager.reconnect_handler(topic, message)
        disconnected_device = self.session_manager.disconnect_handler(topic, message)
        if disconnected_device:
            self.algorithm.device_disconnected(disconnected_device)

    def handle_message(self, topic):
        if topic == "gps/enable":
            if not self.session_manager.is_session_enabled():
                self.session_manager.enable_session()
        elif topic == "gps/disable":
            self.session_manager.disable_session()

    def check_connection(self, topic, message):
        if topic == "esp/connection/connected" and self.session_manager.is_session_enabled():
            out_message = f"device {message} wants to reconnect, proceed?"
            self.mqtt_client.publish("esp/connection/reconnect/allow", out_message)

    def enable_algorithm(self, topic, message):
        if topic == "gps/metric" and self.session_manager.is_session_enabled():
            self.algorithm.process_message(message)
