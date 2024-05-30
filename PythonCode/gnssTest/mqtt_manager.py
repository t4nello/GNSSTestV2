from session_manager import SessionManager
from session_config_manager import SessionConfigManager
from algorithm import Algorithm
import paho.mqtt.client as mqtt

class MqttManager:
    def __init__(self, clientid):
        self.client = mqtt.Client(clientid)
        self.session_config_manager = SessionConfigManager("session_data.json")
        self.session_manager = SessionManager(self, self.session_config_manager)
        self.algoritm = Algorithm(MqttManager,SessionManager)
    def connect(self, host, port):
        self.client.connect(host, port)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        topics_to_subscribe = [
            "gps/#",
            "esp/#"
        ]
        for topic in topics_to_subscribe:
            self.client.subscribe(topic)
        self.set_callback()

    def on_message(self, on_message_callback):
        self.client.on_message = on_message_callback

    def set_callback(self):
        self.client.message_callback_add("gps/algorithm/threshold", self.algoritm.on_threshold_received)
        self.client.message_callback_add("esp/connection/disconnected", self.algoritm.disconnected_device_handler)
        self.client.message_callback_add("gps/metric", self.session_manager.enable_algorithm)
        self.client.message_callback_add("esp/connection/reconnect", self.session_manager.reconnect_handler)
        self.client.message_callback_add("gps/enable", self.session_manager.enable_session) 
        self.client.message_callback_add("gps/disable", self.session_manager.disable_session) 
        self.client.message_callback_add("esp/connection/connected", self.session_manager.process_reconnect_request_mid_session)

    def loop_forever(self):
        self.client.loop_forever()

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
