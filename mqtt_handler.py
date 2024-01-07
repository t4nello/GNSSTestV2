import paho.mqtt.client as mqtt
import  time
class MqttHandler:
    def __init__(self):
        self.client = mqtt.Client()

    def connect(self, host, port):
        self.client.connect(host, port)

    def on_connect(self, on_connect_callback):
        self.client.on_connect = on_connect_callback

    def on_message(self, on_message_callback):
        self.client.on_message = on_message_callback

    def loop_forever(self):
        self.client.loop_forever()

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection. Retrying in 10 seconds...")
            time.sleep(10)
            self.client.reconnect()
