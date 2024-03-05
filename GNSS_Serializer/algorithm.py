import json
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np

class Algorithm:
    def __init__(self, mqtt_handler, session_manager):
        self.window_data = defaultdict(list)
        self.mqtt_handler = mqtt_handler
        self.session_manager = session_manager
        self.device_count = {}
        self.received_measurements = defaultdict(set)
        self.ready_to_process = False
        self.max_deviation_threshold = 0.00003
        self.excluded_devices = set()

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
                self.add_last_coordinates()

        except Exception as e:
            print("Error:", str(e))

    def device_disconnected(self, device):
        disconnected_device = self.session_manager.disconnect_handler("esp/connection/disconnected", device)
        if disconnected_device:
            if disconnected_device in self.device_count:
                del self.device_count[disconnected_device]

    def add_last_coordinates(self):
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
                    first_device_time - timedelta(seconds=3) <= data[-1]["time"] <= first_device_time +
                    timedelta(seconds=3)):
                return

        last_coordinates = defaultdict(dict)
        for device, data in self.window_data.items():
            if data:
                last_coordinates[device]["latitude"] = data[-1]["latitude"]
                last_coordinates[device]["longitude"] = data[-1]["longitude"]

        self.ready_to_process = True
        #print("last cords")
        #for device, coordinates in last_coordinates.items():
        #    print(f"Device: {device}, Latitude: {coordinates['latitude']}")
        #    print(f"Device: {device}, Longitude: {coordinates['longitude']}")
        self.check_device_deviation(last_coordinates)
        self.calculate_average_coordinates(last_coordinates)

    import numpy as np

    def check_device_deviation(self, last_coordinates):
        for device, coordinates in last_coordinates.items():
            if len(self.window_data[device]) >= 8:
                last_four_latitudes = [data["latitude"] for data in self.window_data[device][-8:]]
                last_four_longitudes = [data["longitude"] for data in self.window_data[device][-8:]]

                # Sprawdzenie, czy są dokładnie 8 pomiarów latitudy i longitudy
                if len(last_four_latitudes) == 8 and len(last_four_longitudes) == 8:
                    # Obliczanie odchylenia standardowego dla latitudy i longitudy
                    latitude_std = np.std(last_four_latitudes)
                    longitude_std = np.std(last_four_longitudes)

                    # Wyświetlanie odchylenia standardowego w notacji normalnej
                    print(f"Odchylenie standardowe dla urządzenia {device}:")
                    print("Latitude Std:", "{:.10f}".format(latitude_std))
                    print("Longitude Std:", "{:.10f}".format(longitude_std))

                    # Sprawdzenie, czy odchylenie standardowe przekracza próg
                    if latitude_std > self.max_deviation_threshold or longitude_std > self.max_deviation_threshold:
                        self.mqtt_handler.publish("gps/algorithm/faulted", device)
                        self.excluded_devices.add(device)
                        print(f"dodane  {self.excluded_devices}")

                        # Usuwanie danych urządzenia z last_four_latitudes i last_four_longitudes
                        del self.window_data[device][-8:]

                    elif device in self.excluded_devices:
                        self.mqtt_handler.publish("gps/algorithm/operative", device)
                        self.excluded_devices.remove(device)
                        print(f"usuniete {self.excluded_devices}")
                else:
                    print(f"Za mało pomiarów dla urządzenia {device}")

    def calculate_average_coordinates(self, last_coordinates):
        if not last_coordinates:
            print("Brak danych do przetworzenia.")
            return

        valid_coordinates = [(coords["latitude"], coords["longitude"]) for device, coords in last_coordinates.items() if
                             device not in self.excluded_devices and coords]

        if not valid_coordinates:
            print("Brak danych do przetworzenia.")
            return

        avg_latitude = sum(coord[0] for coord in valid_coordinates) / len(valid_coordinates)
        avg_longitude = sum(coord[1] for coord in valid_coordinates) / len(valid_coordinates)

        self.send_gps_metric_data(avg_latitude, avg_longitude)

    def send_gps_metric_data(self, avg_latitude, avg_longitude):
        if not self.window_data:
            print("Brak danych do przetworzenia.")
            return

        last_speed_values = []
        last_altitude_values = []
        last_satellites_values = []
        last_time_values = []
        last_sessionid_values = []

        for device, data in self.window_data.items():
            if data:
                last_speed_values.append(data[-1]["speed"])
                last_altitude_values.append(data[-1]["altitude"])
                last_satellites_values.append(data[-1]["satellites"])
                last_time_values.append(data[-1]["time"])
                last_sessionid_values.append(data[-1]["sessionid"])

        json_data = {
            "device": "Algorithm",
            "latitude": round(avg_latitude, 7),
            "longitude": round(avg_longitude, 7),
            "speed": round(sum(last_speed_values) / len(last_speed_values), 2),
            "altitude": round(sum(last_altitude_values) / len(last_altitude_values), 2),
            "satellites": max(last_satellites_values),
            "time": max(last_time_values).timestamp(),
            "sessionid": max(last_sessionid_values)
        }

        json_result = json.dumps(json_data, indent=2)
        self.mqtt_handler.publish("gps/metric", json_result)
