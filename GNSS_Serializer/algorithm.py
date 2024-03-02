import json
from collections import defaultdict
from datetime import datetime, timedelta

class Algorithm:
    def __init__(self, mqtt_handler, session_manager):
        self.window_data = defaultdict(list)
        self.mqtt_handler = mqtt_handler
        self.session_manager = session_manager
        self.device_count = {}
        self.received_measurements = defaultdict(set)
        self.ready_to_process = False
        self.max_deviation_threshold = 0.00003  # Threshold for maximum deviation
        self.excluded_devices = set()  # Set to store devices currently excluded from average calculations

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

            if self.session_manager.is_mac_address(device):
                self.device_count[device] = self.device_count.get(device, 0) + 1
                self.window_data[device].append({
                    "latitude": latitude,
                    "longitude": longitude,
                    "speed": speed,
                    "altitude": altitude,
                    "satellites": satellites,
                    "time": time,
                    "sessionid": sessionid
                })

                self.check_device_deviation(device)
                self.add_last_latitude_values()
                self.add_last_longitude_values()
                self.display_average_values()



        except Exception as e:
            print("Error:", str(e))

    def check_device_deviation(self, device):
        if len(self.window_data[device]) >= 6:
            last_four_latitudes = [data["latitude"] for data in self.window_data[device][-4:]]
            last_four_longitudes = [data["longitude"] for data in self.window_data[device][-4:]]
            latitude_deviation = max(last_four_latitudes) - min(last_four_latitudes)
            longitude_deviation = max(last_four_longitudes) - min(last_four_longitudes)

            if latitude_deviation > self.max_deviation_threshold or longitude_deviation > self.max_deviation_threshold:
                print(f"Ostrzeżenie: Odchylenie dla urządzenia {device} jest zbyt duże.")
                self.mqtt_handler.publish("gps/algorithm/faulted", device)
                self.excluded_devices.add(device)
            elif device in self.excluded_devices:
                print(f"Urządzenie {device} wróciło do normy.")
                self.mqtt_handler.publish("gps/algorithm/operative", device )
                self.excluded_devices.remove(device)

    def device_disconnected(self, device):
        disconnected_device = self.session_manager.disconnect_handler("esp/connection/disconnected", device)
        if disconnected_device:
            if disconnected_device in self.device_count:
                del self.device_count[disconnected_device]

    def add_last_latitude_values(self):
        if not self.window_data:
            print("Brak danych do przetworzenia.")
            return


        first_device_time = None
        for device, data in self.window_data.items():
            if data:
                first_device_time = data[-1]["time"]
                break

        for device, data in self.window_data.items():
            if not data or not (
                    first_device_time - timedelta(seconds=3) <= data[-1]["time"] <= first_device_time + timedelta(
                    seconds=3)):

                return

        # Dodaj ostatnie wartości latitude dla każdego urządzenia
        last_latitude_values = {}
        for device, data in self.window_data.items():
            last_latitude_values[device] = data[-1]["latitude"]
        self.ready_to_process = True

    def add_last_longitude_values(self):
        # Sprawdź, czy istnieją dane do przetworzenia
        if not self.window_data:
            print("Brak danych do przetworzenia.")
            return

        first_device_time = None
        for device, data in self.window_data.items():
            if data:
                first_device_time = data[-1]["time"]
                break

        for device, data in self.window_data.items():
            if not data or not (
                    first_device_time - timedelta(seconds=3) <= data[-1]["time"] <= first_device_time + timedelta(
                seconds=3)):

                return

        last_longitude_values = {}
        for device, data in self.window_data.items():
            last_longitude_values[device] = data[-1]["longitude"]
        self.ready_to_process = True

    def display_average_values(self):
        if not self.window_data:
            print("Brak danych do przetworzenia.")
            return

        last_latitude_values = []
        last_longitude_values = []
        for device, data in self.window_data.items():
            if data and device not in self.excluded_devices:
                last_latitude_values.append(data[-1]["latitude"])
                last_longitude_values.append(data[-1]["longitude"])

        if not last_latitude_values or not last_longitude_values:
            print("Brak danych do przetworzenia.")
            return


        avg_latitude = sum(last_latitude_values) / len(last_latitude_values)
        avg_longitude = sum(last_longitude_values) / len(last_longitude_values)

        self.send_gps_metric_data(avg_latitude, avg_longitude)

    def send_gps_metric_data(self,avg_latitude, avg_longitude):
        if not self.window_data:
            print("Brak danych do przetworzenia.")
            return

        last_latitude_values = []
        last_longitude_values = []
        last_speed_values = []
        last_altitude_values = []
        last_satellites_values = []
        last_time_values = []
        last_sessionid_values = []

        for device, data in self.window_data.items():
            if data:
                last_latitude_values.append(data[-1]["latitude"])
                last_longitude_values.append(data[-1]["longitude"])
                last_speed_values.append(data[-1]["speed"])
                last_altitude_values.append(data[-1]["altitude"])
                last_satellites_values.append(data[-1]["satellites"])
                last_time_values.append(data[-1]["time"])
                last_sessionid_values.append(data[-1]["sessionid"])

        json_data = {
            "device": "Algorithm",
            "latitude": round(sum(last_latitude_values) / len(last_latitude_values),7),
            "longitude": round(sum(last_longitude_values) / len(last_longitude_values), 7),
            "speed": round(sum(last_speed_values) / len(last_speed_values), 2),
            "altitude": round(sum(last_altitude_values) / len(last_altitude_values), 2),
            "satellites": max(last_satellites_values),
            "time": max(last_time_values).timestamp(),
            "sessionid": max(last_sessionid_values)
        }

        json_result = json.dumps(json_data, indent=2)
        self.mqtt_handler.publish("gps/metric", json_result)