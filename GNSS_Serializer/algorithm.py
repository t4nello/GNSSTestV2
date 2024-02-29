import json
from datetime import datetime
from collections import defaultdict
import  re
class Algorithm:
    def __init__(self, mqtt_handler,session_manger):
        self.window_data = defaultdict(list)
        self.mqtt_handler = mqtt_handler
        self.session_manager = session_manger
        self.device_count = {}

    def is_mac_address(self, address):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(address))

    def process_message(self, msg):
        try:
            device_data = json.loads(msg)
            device = device_data["device"]
            latitude = device_data["latitude"]
            longitude = device_data["longitude"]
            speed = device_data["speed"]
            altitude = device_data["altitude"]
            satellites = device_data["satellites"]
            time = datetime.fromtimestamp(device_data["time"])
            sessionid = device_data["sessionid"]

            if self.is_mac_address(device):
                # Dodaj lub aktualizuj liczbę wystąpień urządzenia
                self.device_count[device] = self.device_count.get(device, 0) + 1
            else:
                print("Niepoprawny adres MAC:", device)


            print("Liczba unikalnych adresów MAC:", len(self.device_count))

        except Exception as e:
            print("Error:", str(e))

    def device_disconnected(self, device):
        disconnected_device = self.session_manager.disconnect_handler("esp/connection/disconnected",device)
        if disconnected_device:
            # Sprawdzenie czy odłączone urządzenie jest w device_count
            if disconnected_device in self.device_count:
                del self.device_count[disconnected_device]
                print(
                    f"Urządzenie {disconnected_device} zostało odłączone. Aktualizacja liczby unikalnych adresów MAC.")
