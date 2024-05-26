from flask import Flask, jsonify, request, g

class Router:
<<<<<<< HEAD
    def __init__(self, postgres_manager, measurand_api):
        self.postgres_manager = postgres_manager
        self.measurand_api = measurand_api(self.postgres_manager)
=======
    def __init__(self, postgres_manager):
        self.postgres_manager = postgres_manager
>>>>>>> origin/master

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
<<<<<<< HEAD

        @app.route('/api/avg/<sessionid>', methods=['GET'])
        def get_average_values(sessionid):
            average_position_data = self.measurand_api.calculate_average_position(sessionid)
            if average_position_data:
                return jsonify(average_position_data)
            else:
                return jsonify({"error": "No average position data available for this session."}), 404

        @app.route('/api/mode/<sessionid>', methods=['GET'])
        def get_most_frequent_position(sessionid):
            most_frequent_position = self.measurand_api.most_frequent_position(sessionid)
            if most_frequent_position:
                return jsonify({"most_frequent_position": most_frequent_position})
            else:
                return jsonify({"error": "No position data available for this session."}), 404

        @app.route('/api/sigma/<sessionid>/<reference_type>', methods=['GET'])
        def get_sigma(sessionid, reference_type):
            try:
                sigma_values = self.measurand_api.calculate_sigma(sessionid, reference_type)
                if sigma_values:
                    return jsonify(sigma_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @app.route('/api/drms/<sessionid>/<reference_type>', methods=['GET'])
        def get_drms(sessionid, reference_type):
            try:
                drms_values = self.measurand_api.calculate_drms(sessionid, reference_type)
                if drms_values:
                    return jsonify(drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @app.route('/api/2drms/<sessionid>/<reference_type>', methods=['GET'])
        def get_2drms(sessionid, reference_type):
            try:
                two_drms_values = self.measurand_api.calculate_2drms(sessionid, reference_type)
                if two_drms_values:
                    return jsonify(two_drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
                
        @app.route('/api/cep/<sessionid>/<reference_type>', methods=['GET'])
        def get_cep(sessionid, reference_type):
            try:
                cep_values = self.measurand_api.calculate_cep(sessionid, reference_type)
                if cep_values:
                    return jsonify(cep_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
=======
>>>>>>> origin/master
