import json
import re

class SessionManager:
    def __init__(self, mqtt_manager, config_manager):
        self.mqtt_manager = mqtt_manager
        self.config_manager = config_manager
        #self.setup_mqtt()

    def enable_session(self):
        if self.get_session_status() == "stopped":
            self.config_manager.config["sessionId"] += 1
            self.config_manager.config["status"] = "started"
            self.config_manager.save_config(self.config_manager.config)
            payload = self.config_manager.config["sessionId"]
            session_id = json.dumps(payload)
            self.mqtt_manager.publish_message("gps/metric/enable", session_id)
            return payload 
        else:
            return "Session already running"

    def disable_session(self):
        if self.get_session_status() == "started":
            self.config_manager.config["status"] = "stopped"
            self.mqtt_manager.publish_message("gps/metric/disable", payload=None)
            self.config_manager.save_config(self.config_manager.config)
            return True
        else:
            return False

    def get_session_status(self):
        return self.config_manager.config.get("status", "stopped") 
    
    def is_valid_mac(self, mac_address):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac_address))
    



