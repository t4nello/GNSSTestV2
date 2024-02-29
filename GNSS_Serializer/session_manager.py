import json

class SessionManager:
    def __init__(self, mqtt_handler, config_manager):
        self.mqtt_handler = mqtt_handler
        self.config_manager = config_manager

    def enable_session(self):
        if not self.is_session_enabled():
            self.config_manager.config["session_number"] += 1
            self.config_manager.config["session_status"] = "started"
            self.config_manager.save_config(self.config_manager.config)

            payload = self.config_manager.config["session_number"]
            session_id = json.dumps(payload)
            session_status = json.dumps("started")
            self.publish_session_info("gps/metric/enable", session_id)
            self.publish_session_info("gps/metric/status", session_status)
            self.publish_session_info("esp/connection/connected", "Algorithm")

    def disable_session(self):
        if self.is_session_enabled():
            self.config_manager.config["session_status"] = "stopped"
            session_status = json.dumps("stopped")
            self.publish_session_info("gps/metric/disable")
            self.publish_session_info("gps/metric/status", session_status)
            self.config_manager.save_config(self.config_manager.config)

    def is_session_enabled(self):
        return self.config_manager.config.get("session_status") == "started"

    def disconnect_handler(self, topic, message):
        if topic == "esp/connection/disconnected":
            device = message
            return device

    def reconnect_handler(self, topic, message):
        if topic == "esp/connection/reconnect" and message == "Yes":
            payload = self.config_manager.config["session_number"]
            session_id = json.dumps(payload)
            self.publish_session_info("gps/metric/enable", session_id)

    def publish_session_info(self, topic, payload=None):
        if payload:
            self.mqtt_handler.publish(topic, payload)
        else:
            self.mqtt_handler.publish(topic)
