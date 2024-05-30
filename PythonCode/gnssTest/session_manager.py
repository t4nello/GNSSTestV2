from algorithm import Algorithm
import json
import re

class SessionManager:
    def __init__(self, mqtt_handler, config_manager):
        self.mqtt_handler = mqtt_handler
        self.config_manager = config_manager
        self.algorithm = Algorithm(mqtt_handler, self)
        
    def enable_session(self, client, userdata, message):
        if not self.is_session_enabled():
            self.config_manager.config["sessionId"] += 1
            self.config_manager.config["status"] = "started"
            self.config_manager.save_config(self.config_manager.config)
            payload = self.config_manager.config["sessionId"]
            session_id = json.dumps(payload)
            session_status = json.dumps("started")
            self.mqtt_handler.publish("gps/metric/enable", session_id)
            self.mqtt_handler.publish("gps/metric/status", session_status)
           

    def disable_session (self, client, userdata, message):
        if  self.is_session_enabled():
            self.config_manager.config["status"] = "stopped"
            session_status = json.dumps("stopped")
            self.mqtt_handler.publish("gps/metric/disable", payload = None)
            self.mqtt_handler.publish("gps/metric/status", session_status)
            self.config_manager.save_config(self.config_manager.config)

    def is_session_enabled(self):
        return self.config_manager.config.get("status") == "started"

    def process_reconnect_request_mid_session(self, client, userdata, message):
        message = message.payload.decode("utf-8")
        if self.is_session_enabled() and self.is_mac_address(message):
            out_message = f"Device {message} wants to reconnect, allow?"
            self.mqtt_handler.publish("esp/connection/reconnect/allow", out_message)

    def is_mac_address(self, message):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(message))
    
    def reconnect_handler(self,client, userdata, message):
        message = message.payload.decode("utf-8")
        if message == "Yes":
            payload = self.config_manager.config["sessionId"]
            session_id = json.dumps(payload)
            self.mqtt_handler.publish("gps/metric/enable", session_id)
    
    def enable_algorithm(self, userdata, topic, message):
            message = message.payload.decode("utf-8")
            self.algorithm.process_message(message)