import json
import re
class Algorithm:
    def __init__(self, mqtt_handler):
        self.messages = []
        self.mqtt_handler = mqtt_handler
        self.unique_mac_addresses = set()




    def process_message(self, message):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        decoded_message = json.loads(message)
        self.messages.append(decoded_message)

        if mac_pattern.match(decoded_message.get("device")):
            self.unique_mac_addresses.add(decoded_message.get("device"))
        unique_mac_count = len(self.unique_mac_addresses)
        messages_processed = unique_mac_count
        if len(self.messages) == messages_processed:
            if all("latitude" in msg for msg in self.messages):
                latitude_avg = round(sum(msg["latitude"] for msg in self.messages) / unique_mac_count, 6)
                longitude_avg = round(sum(msg["longitude"] for msg in self.messages) / unique_mac_count, 6)
                speed = round(sum(msg["speed"] for msg in self.messages) / unique_mac_count, 2)
                altitude = round(sum(msg["altitude"] for msg in self.messages) / unique_mac_count, 2)
                satellites = max(msg["satellites"] for msg in self.messages)
                max_time = max(msg["time"] for msg in self.messages)

                result_json = {
                    "device": "Algorithm",
                    "latitude": latitude_avg,
                    "longitude": longitude_avg,
                    "speed": speed,
                    "altitude": altitude,
                    "satellites": satellites,
                    "time": max_time,
                    "sessionid": decoded_message.get("sessionid")
                }

                self.mqtt_handler.publish("gps/metric", json.dumps(result_json))
                print(result_json)
                print(self.unique_mac_addresses)
                print(unique_mac_count)
            self.messages = []
