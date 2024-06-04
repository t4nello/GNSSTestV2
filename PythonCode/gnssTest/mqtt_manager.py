from blinker import Signal
from flask_mqtt import Mqtt
from algorithm import Algorithm

class MqttManager:
    device_connected = Signal()
    device_disconnected = Signal()
    
    def __init__(self, app):
        self.app = app
        self.mqtt = Mqtt(self.app)
        self.algoritm = Algorithm(MqttManager)
        self.app.config['MQTT_CLIENT_ID'] = 'python'
        self.app.config['MQTT_BROKER_URL'] = 'localhost'
        self.app.config['MQTT_BROKER_PORT'] = 1883
        self.setup_mqtt()
    
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.setup_mqtt()

    def setup_mqtt(self):
        @self.mqtt.on_connect()
        def handle_connect(client, userdata, flags, rc):
            self.mqtt.subscribe('esp/#')
            self.mqtt.subscribe('gps/#')
        
        @self.mqtt.on_topic('esp/connection/connected')
        def handle_connected_device(client, userdata, message):
            payload = message.payload.decode("utf-8")
            self.connected_device(payload) 

        @self.mqtt.on_topic('esp/connection/disconnected')
        def handle_disconnected_device(client, userdata, message):
            payload = message.payload.decode("utf-8")
            self.disconnected_device(payload)  
        
        @self.mqtt.on_topic('gps/metric')
        def pass_data_to_algorithm(client, userdata, message):
            payload = message.payload.decode("utf-8")
            self.algorithm.process_message(payload)
            
    def connected_device(self, device):
        self.device_connected.send(device=device)
        return device
   
    def disconnected_device(self, device):
       self.device_disconnected.send(device=device)
       return device 

    def publish_message(self, topic, payload):  
        self.mqtt.publish(topic, payload)

    def detect_device(self, address):
       self.publish_message("esp/detect", address)
