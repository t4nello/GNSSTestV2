from flask_mqtt import Mqtt

class MqttManager:
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
            
    def publish_message(self, topic, payload):
        self.mqtt.publish(topic, payload)