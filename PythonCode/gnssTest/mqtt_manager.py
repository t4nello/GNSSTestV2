from blinker import Signal
from flask_mqtt import Mqtt


class MqttManager:
    devices_changed = Signal()

    def __init__(self, app):
        self.app = app
        self.mqtt = Mqtt(self.app)
        self.app.config['MQTT_CLIENT_ID'] = 'python'
        self.app.config['MQTT_BROKER_URL'] = 'localhost'
        self.app.config['MQTT_BROKER_PORT'] = 1883
        self.setup_mqtt()
        self.connected_devices = set()  

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
                self.add_connected_device(payload) 
            elif topic == 'esp/connection/disconnected':
                self.remove_connected_device(payload)  

    def add_connected_device(self, device):
        self.connected_devices.add(device)
        self.devices_changed.send()

    def remove_connected_device(self, device):
        if device in self.connected_devices:
            self.connected_devices.remove(device)
            self.devices_changed.send()
            
    def get_connected_devices(self):
        return list(self.connected_devices)
