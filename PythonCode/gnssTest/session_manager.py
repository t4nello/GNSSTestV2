import json
import re
import requests

class SessionManager:
    def __init__(self, mqtt_manager, config_manager):
        self.mqtt_manager = mqtt_manager
        self.config_manager = config_manager
        self.setup_mqtt()

    def enable_session(self):
        if self.get_session_status() == "stopped":
            self.config_manager.config["sessionId"] += 1
            self.config_manager.config["status"] = "started"
            self.config_manager.save_config(self.config_manager.config)
            payload = self.config_manager.config["sessionId"]
            session_id = json.dumps(payload)
            session_status = json.dumps("started")
            self.mqtt_manager.publish_message("gps/metric/enable", session_id)
            self.mqtt_manager.publish_message("gps/metric/status", session_status)
            return payload 
        else:
            return "Session already running"

    def disable_session(self):
        if self.get_session_status() == "started":
            self.config_manager.config["status"] = "stopped"
            session_status = json.dumps("stopped")
            self.mqtt_manager.publish_message("gps/metric/disable", payload=None)
            self.mqtt_manager.publish_message("gps/metric/status", session_status)
            self.config_manager.save_config(self.config_manager.config)
            return "Session stopped successfully"
        else:
            return "Session is already stopped"

    def get_session_status(self):
        return self.config_manager.config.get("status", "stopped") 
    
    def is_valid_mac(self, mac_address):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac_address))

    def setup_mqtt(self):
         @self.mqtt_manager.mqtt.on_topic('esp/connection/connected')
         def handle_connection_topic(client, userdata, message):
            mac_address = message.payload.decode()
            if self.is_valid_mac(mac_address):
                self.handle_mac_address(mac_address)

    def handle_mac_address(self, mac_address):
        if self.get_session_status() == "stopped":
            self.enable_session()
