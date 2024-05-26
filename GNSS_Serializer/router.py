from flask import Flask, jsonify, request, g

class Router:
    def __init__(self, postgres_manager):
        self.postgres_manager = postgres_manager

    def configure_routes(self, app):
        @app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            unique_session_ids = self.postgres_manager.get_unique_session_ids()
            return jsonify({"sessions": unique_session_ids})

        @app.route('/api/devices', methods=['GET'])
        def get_devices():
            unique_devices = self.postgres_manager.get_unique_devices()
            return jsonify({"devices": unique_devices})

        @app.route('/api/<device>/<field>/<sessionid>', methods=['GET'])
        def get_data(device, field, sessionid):
            valid_fields = ["latitude", "longitude", "position", "speed", "satellites", "altitude"]
            if field not in valid_fields:
                    return jsonify({"error": "Invalid field"}), 400
            if device == "all":
                if field == "position":
                    data = self.postgres_manager.get_position_for_session(sessionid)
                else:
                    data = self.postgres_manager.get_measurand_for_device(field, sessionid)
            else:
                if field == "position":
                    data = self.postgres_manager.get_position_for_device(device, sessionid)
                else: 
                    data = self.postgres_manager.get_measurand_for_session(device, field ,sessionid)
            if data is not None:
                return jsonify(data)
            else:
                return jsonify({"error": "Invalid request or missing data"}), 400  

        @app.route('/api/<session>/devices', methods=['GET'])
        def get_devices_per_session(session):
            unique_devices = self.postgres_manager.get_unique_devices_per_session(session)
            return jsonify({"devices": unique_devices})
