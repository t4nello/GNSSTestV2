import json
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
from scipy.signal import savgol_filter


class Algorithm:
    def __init__(self):
        self.window_data = defaultdict(list)  # Store data for each device
        self.device_count = {}  # Count of messages received from each device
        self.received_measurements = defaultdict(set)  # Store received measurements
        self.ready_to_process = False  # Flag indicating if data is ready for processing
        self.max_deviation_threshold = 0.000055  # Maximum deviation threshold
        self.excluded_devices = set()  # Set of excluded devices
        self.latitude_window_avg_array = []  # Array to store latitude window averages
        self.longitude_window_avg_array = []  # Array to store longitude window averages
    def process_message(self, message):
        try:
            # Process incoming message
            device_data = json.loads(message)
            device = device_data["device"]
            latitude = device_data["latitude"]
            longitude = device_data["longitude"]
            speed = device_data["speed"]
            altitude = device_data["altitude"]
            satellites = device_data["satellites"]
            time = datetime.fromtimestamp(device_data["time"])
            sessionid = device_data["sessionid"]

            if self.session_manager.is_mac_address(device):
                # Update device count and window data
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
                self.add_last_coordinates()  # Check if data is ready for processing

        except Exception as e:
            print("Error:", str(e))
        
    def on_threshold_received(self, message):
        try:
            self.max_deviation_threshold = message
        except ValueError as ve:
            print(f"Error processing threshold: {ve}")
            self.max_deviation_threshold = 0.000055
        
    
    def disconnected_device_handler(self, client, userdata, message):
        device_id = message.payload.decode("utf-8")
        if device_id in self.window_data:
            del self.window_data[device_id]
            if device_id in self.device_count:
                del self.device_count[device_id]
            if device_id in self.excluded_devices:
                self.excluded_devices.remove(device_id)
            print(f"Device {device_id} disconnected. Stopped processing data from this device.")
        else:
            print(f"Unknown device: {device_id}.")


    def add_last_coordinates(self):
        # Add last coordinates to the processing window
        if not self.window_data:
            print("No data to process.")
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
        self.check_device_deviation(last_coordinates)  # Check for device deviation
        self.calculate_average_coordinates(last_coordinates)  # Calculate average coordinates

    def check_device_deviation(self, last_coordinates):
        print(self.max_deviation_threshold)
        for device, coordinates in last_coordinates.items():
            if device not in self.window_data:
                self.window_data[device] = []
                self.window_data[device].extend(coordinates[-4:])

            if len(self.window_data[device]) >= 4:
                last_four_latitudes = [data["latitude"] for data in self.window_data[device][-4:]]
                last_four_longitudes = [data["longitude"] for data in self.window_data[device][-4:]]

                # Obliczanie odchylenia standardowego dla latitudy i longitudy
                latitude_std = np.std(last_four_latitudes)
                longitude_std = np.std(last_four_longitudes)

                # Sprawdzenie, czy odchylenie standardowe przekracza próg
                if latitude_std > self.max_deviation_threshold or longitude_std > self.max_deviation_threshold:
                    self.excluded_devices.add(device)
                    print(f"Dodane: {self.excluded_devices}")
                    self.window_data[device] = []

                elif device in self.excluded_devices:
                    self.excluded_devices.remove(device)
                    print(f"Usunięte: {self.excluded_devices}")
            else:
                print(f"Za mało pomiarów dla urządzenia {device}")

    def calculate_average_coordinates(self, last_coordinates):
        # Calculate average coordinates
        if not last_coordinates:
            print("No data to process.")
            return

        valid_coordinates = [(coords["latitude"], coords["longitude"]) for device, coords in last_coordinates.items() if
                             device not in self.excluded_devices and coords]
        if not valid_coordinates:
            print("No data to process.")
            return

        # Smoothing data using moving average
        latitude_window_avg = sum(coord[0] for coord in valid_coordinates) / len(valid_coordinates)
        longitude_window_avg = sum(coord[1] for coord in valid_coordinates) / len(valid_coordinates)

        self.latitude_window_avg_array.append(latitude_window_avg)
        self.longitude_window_avg_array.append(longitude_window_avg)
        if len(self.latitude_window_avg_array) >= len(valid_coordinates):
            # Smoothing data using Savitzky-Golay filter
            smoothed_latitude_sg = savgol_filter(self.latitude_window_avg_array, window_length=len(valid_coordinates),
                                                polyorder= len(valid_coordinates)-1)
            smoothed_longitude_sg = savgol_filter(self.longitude_window_avg_array, window_length=len(valid_coordinates),
                                                  polyorder= len(valid_coordinates)-1)

            # Calculate average coordinates after smoothing
            avg_latitude = sum(smoothed_latitude_sg) / len(smoothed_latitude_sg)
            avg_longitude = sum(smoothed_longitude_sg) / len(smoothed_longitude_sg)

            # Send GPS metric data
            self.send_gps_metric_data(avg_latitude, avg_longitude)
            self.latitude_window_avg_array = self.latitude_window_avg_array[-len(valid_coordinates)-3:]
            self.longitude_window_avg_array = self.longitude_window_avg_array[-len(valid_coordinates)-3:]

    def send_gps_metric_data(self, avg_latitude, avg_longitude):
        # Send GPS metric data
        if not self.window_data:
            print("No data to process.")
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

        json_result = json.dumps(json_data)
        self.mqtt_handler.publish("gps/metric", json_result)
