import paho.mqtt.client as mqtt
from flask import Flask
from GNSS_Serializer.DatabaseManager import PostgresDBManager
from gps_metric_handler import GpsMetricHandler
from config_manager import ConfigManager
from session_manager import SessionManager
from algorithm import Algorithm
from router import Router
def main():
    config_manager = ConfigManager("config.json")
    id = "gnssSerializer"
    mqtt_handler = mqtt.Client(id)
    session_manager = SessionManager(mqtt_handler, config_manager)
    algorithm_instance = Algorithm(mqtt_handler, session_manager)
    gps_handler = GpsMetricHandler(mqtt_handler, config_manager, session_manager, algorithm_instance)

    mqtt_handler.on_connect = gps_handler.on_connect
    mqtt_handler.on_message = gps_handler.on_message

    mqtt_handler.connect("192.168.0.213", 1883)

    router = Router(PostgresDBManager("host=localhost user=postgres password=admin123 dbname=tsdb"))
    app = Flask(__name__)
    router.configure_routes(app)
    app.run(debug=True)

    mqtt_handler.loop_forever()

if __name__ == "__main__":
    main()
