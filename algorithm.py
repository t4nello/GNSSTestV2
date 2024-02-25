import json
import re
import pandas as pd

class Algorithm:
    def __init__(self, mqtt_handler):
        self.df = pd.DataFrame(columns=['latitude', 'longitude', 'speed', 'altitude', 'satellites', 'time', 'sessionid', 'device'])
        self.mqtt_handler = mqtt_handler

    def process_message(self, message):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        decoded_message = json.loads(message)

        if mac_pattern.match(decoded_message.get("device")):
            self.df = self.df.append(decoded_message, ignore_index=True)  # Add a new measurement to the DataFrame

        if len(self.df) >= 10:  # Process when DataFrame has 10 or more measurements
            if all(key in self.df.columns for key in ['latitude', 'longitude', 'speed', 'altitude', 'satellites', 'time', 'sessionid', 'device']):
                # Check deviation and remove faulty devices
                self.check_deviation()

                latitude_values = self.df['latitude'].tolist()
                longitude_values = self.df['longitude'].tolist()
                smoothed_latitude = self.calculate_dynamic_ma(latitude_values)
                smoothed_longitude = self.calculate_dynamic_ma(longitude_values)

                result_json = {
                    "device": "Algorithm",
                    "latitude": smoothed_latitude[-1],  # Use the latest smoothed value
                    "longitude": smoothed_longitude[-1],  # Use the latest smoothed value
                    "speed": self.df['speed'].mean(),
                    "altitude": self.df['altitude'].mean(),
                    "satellites": self.df['satellites'].max(),
                    "time": self.df['time'].max(),
                    "sessionid": self.df['sessionid'].iloc[0]  # Use the sessionid from the first measurement
                }

                self.mqtt_handler.publish("gps/metric", json.dumps(result_json))
                print(result_json)
                self.df = pd.DataFrame(columns=['latitude', 'longitude', 'speed', 'altitude', 'satellites', 'time', 'sessionid', 'device'])

    def check_deviation(self):
        # Calculate mean latitude and longitude
        mean_latitude = self.df['latitude'].mean()
        mean_longitude = self.df['longitude'].mean()

        # Calculate deviation for each device
        for device, group in self.df.groupby('device'):
            device_latitude_deviation = abs(group['latitude'].mean() - mean_latitude)
            device_longitude_deviation = abs(group['longitude'].mean() - mean_longitude)

            # If deviation is too large, remove the device from DataFrame and send faulted message
            if device_latitude_deviation > 0.005 or device_longitude_deviation > 0.005:
                self.df = self.df[self.df['device'] != device]  # Remove faulty device from DataFrame
                self.mqtt_handler.publish("gps/faulted", device)
                print(f"Faulty device detected: {device}")

    def calculate_dynamic_ma(self, data):
        window_size = min(10, len(data))
        try:
            rolling_mean = pd.to_numeric(data, errors='coerce').rolling(window=window_size, min_periods=1).mean()
        except Exception as e:
            print(f"Error calculating rolling mean: {e}")
            rolling_mean = pd.Series(data)
        return rolling_mean.tolist()
