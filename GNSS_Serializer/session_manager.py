# session_manager.py
import json
class SessionManager:
    def __init__(self, mqtt_handler, config_manager):
        self.mqtt_handler = mqtt_handler
        self.config_manager = config_manager

    def enable_session(self):
        if not self.is_session_enabled():
            self.config_manager.config["session_number"] += 1
            self.config_manager.config["session_status"] = "started"
            self.config_manager.save_config()

            payload = self.config_manager.config["session_number"]
            session_id = json.dumps(payload)
            session_status = json.dumps("started")

            self.mqtt_handler.publish("gps/metric/enable", session_id)
            self.mqtt_handler.publish("gps/metric/status", session_status)
            self.mqtt_handler.publish("esp/connection/connected", "Algorithm")

    def disable_session(self):
        if self.is_session_enabled():
            self.config_manager.config["session_status"] = "stopped"
            session_status = json.dumps("stopped")
            self.mqtt_handler.publish("gps/metric/status", session_status)
            self.config_manager.save_config()

    def is_session_enabled(self):
        return self.config_manager.config.get("session_status") == "started"
