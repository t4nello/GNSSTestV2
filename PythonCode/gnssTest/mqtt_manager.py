from blinker import Signal
from flask_mqtt import Mqtt

class MqttManager:
    device_connected = Signal()
    device_disconnected = Signal()
    
    def __init__(self, app):
        self.app = app
        self.mqtt = Mqtt(self.app)
        self.app.config['MQTT_CLIENT_ID'] = 'python'
        self.app.config['MQTT_BROKER_URL'] = 'localhost'
        self.app.config['MQTT_BROKER_PORT'] = 1883
        self.setup_mqtt()

    def setup_mqtt(self):
        @self.mqtt.on_connect()
        def handle_connect(client, userdata, flags, rc):
            self.mqtt.subscribe('esp/#')
            self.mqtt.subscribe('gps/#')
        
        @self.mqtt.on_message()
        def handle_message(client, userdata, message):
            topic = message.topic
            payload = message.payload.decode("utf-8")
            if topic == 'esp/connection/connected':
                self.connected_device(payload) 
            elif topic == 'esp/connection/disconnected':
                self.disconnected_device(payload)  

    def connected_device(self, device):
        self.device_connected.send(device=device)
        return device
   
    def disconnected_device(self, device):
       self.device_disconnected.send(device=device)
       return device 

    def publish_message(self, topic, payload=None):  
        self.mqtt.publish(topic, payload)

    @staticmethod
    def detect_device(address):
       Mqtt.publish("esp/detect", address)
