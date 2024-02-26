# gps_metric_handler.py

import json

class GpsMetricHandler:
    def __init__(self, mqtt_client, config_manager, session_manager, algorithm):
        self.mqtt_client = mqtt_client
        self.config_manager = config_manager
        self.session_manager = session_manager
        self.algorithm = algorithm

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.mqtt_client.subscribe("gps/metric")
        self.mqtt_client.subscribe("gps/metric/+")
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        self.handle_message(topic)
        self.enable_algorithm(topic,message)
    def handle_message(self, topic):
        if topic == "gps/metric/enable":
            if not self.session_manager.is_session_enabled():
                self.session_manager.enable_session()
        elif topic == "gps/metric/disable":
            self.session_manager.disable_session()

    def enable_algorithm(self, topic, message):
        if topic == "gps/metric" and self.session_manager.is_session_enabled():
            self.algorithm.process_message(message)
