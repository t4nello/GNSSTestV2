from statistics import mode, stdev
from pyproj import Proj, Transformer
import math
class MeasurandCalculator:

    def __init__(self, postgres_manager):
        self.postgres_manager = postgres_manager
      
    def calculate_average_position(self, sessionid):
        values = self.postgres_manager.get_position_for_session(sessionid)
        if not values:
            return None
        
        total_latitude = sum(entry["latitude"] for entry in values)
        total_longitude = sum(entry["longitude"] for entry in values)
        count = len(values)

        average_latitude = round(total_latitude / count, 6)
        average_longitude = round(total_longitude / count, 6)

        average_position = (average_latitude, average_longitude)
        return average_position

    def most_frequent_position(self, sessionid):
        values = self.postgres_manager.get_position_for_session(sessionid)
        if not values:
            return None

        positions_list = [(entry["latitude"], entry["longitude"]) for entry in values]
        most_common_position = mode(positions_list)
        return most_common_position

    def convert_lat_lon_to_utm(self, positions):
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633")
        utm_coordinates = []
        for position in positions:
            latitude, longitude = position
            utm_x, utm_y = transformer.transform(longitude, latitude)
            utm_coordinates.append((round(utm_x, 6), round(utm_y, 6)))
        return utm_coordinates

    def calculate_sigma(self, sessionid, reference):
        values = self.postgres_manager.get_position_for_session(sessionid)
        if not values:
            return None
        
        if ',' in reference:
            reference_position = tuple(map(float, reference.split(',')))
            reference_position = self.convert_lat_lon_to_utm([reference_position])
        else:
            if reference == 'avg':
                reference_position = self.calculate_average_position(sessionid)
                reference_position = self.convert_lat_lon_to_utm([reference_position])
            elif reference == 'mode':
                reference_position = self.most_frequent_position(sessionid)
                reference_position = self.convert_lat_lon_to_utm([reference_position])
            else:
                raise ValueError("Nieprawidłowy typ referencji. Dostępne opcje: 'avg' lub 'mode'.")

            if reference_position is None:
                return None

        measurements_by_device = {}
        for entry in values:
            device = entry["device"]
            if device not in measurements_by_device:
                measurements_by_device[device] = []
            measurements_by_device[device].append((entry["latitude"], entry["longitude"]))

        sigma_values = {}
        for device, measurements in measurements_by_device.items():
            utm_coordinates = self.convert_lat_lon_to_utm(measurements)
            L = len(measurements) 
            sigma_latitude = math.sqrt(sum((utm[0] - reference_position[0][0])**2 for utm in utm_coordinates) / (L - 1))
            sigma_longitude = math.sqrt(sum((utm[1] - reference_position[0][1])**2 for utm in utm_coordinates) / (L - 1))
            sigma_values[device] = (sigma_latitude, sigma_longitude)
        return sigma_values

    def calculate_drms(self, sessionid, reference_type):
        sigma_values = self.calculate_sigma(sessionid, reference_type)
        if sigma_values is None:
            return None

        drms_values = {}
        for device, sigma in sigma_values.items():
            sigma_north, sigma_east = sigma
            drms = math.sqrt(sigma_north**2 + sigma_east**2)
            drms_values[device] = round(drms, 2)
        return drms_values

    def calculate_2drms(self, sessionid, reference_type):
        drms_values = self.calculate_drms(sessionid, reference_type)
        if drms_values is None:
            return None

        drms_2x_values = {}
        for device, drms in drms_values.items():
            drms_2x = 2 * drms
            drms_2x_values[device] = round(drms_2x, 2)
        return drms_2x_values
    
    def calculate_cep(self, sessionid, reference_type):
        sigma_values = self.calculate_sigma(sessionid, reference_type)
        if sigma_values is None:
            return None

        cep_values = {}
        for device, sigma in sigma_values.items():
            sigma_north, sigma_east = sigma
            cep = 0.652 * sigma_north + 0.56 * sigma_east
            cep_values[device] = round(cep, 2)
        return cep_values


