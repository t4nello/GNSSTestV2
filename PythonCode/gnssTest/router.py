from flask import jsonify
from session_manager import SessionManager

class Router:
    def __init__(self, app, mqtt_manager, config_manager, data_processor, measurand_calculator):
        self.app = app
        self.session_manager = SessionManager(mqtt_manager, config_manager)
        self.data_processor = data_processor
        self.measurand_calculator = measurand_calculator(self.data_processor)
        self.setup_routes()
        self.valid_fields = ["latitude", "longitude", "position", "speed", "satellites", "altitude"]


    def setup_routes(self):
        @self.app.route('/api/session/start')
        def start_session():
            result = self.session_manager.enable_session()
            if isinstance(result, int):
                return jsonify({"session_id": result}), 200
            else:
                return jsonify({"error": result}), 400

        @self.app.route('/api/session/stop')
        def stop_session():
            result = self.session_manager.disable_session()
            if result == "Session stopped successfully":
                return "OK", 200
            else:
                return jsonify({"error": result}), 400

        @self.app.route('/api/session/status')
        def get_session_status():
            result = self.session_manager.get_session_status()
            jsonify({"error": result}), 200
            
        @self.app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            unique_session_ids = self.data_processor.get_unique_session_ids()
            return jsonify({"sessions": unique_session_ids})

        @self.app.route('/api/devices', methods=['GET'])
        def get_devices():
            unique_devices = self.data_processor.get_unique_devices()
            return jsonify({"devices": unique_devices})

        @self.app.route('/api/data/<sessionid>/<device>/<field>', methods=['GET'])
        def get_data(device, field, sessionid):
            if field not in self.valid_fields:
                return jsonify({"error": "Invalid field"}), 400
            if device == "all":
                if field == "position":
                    data = self.data_processor.get_position_for_session(sessionid)
                else:
                    data = self.data_processor.get_measurand_for_device(field, sessionid)
            else:
                if field == "position":
                    data = self.data_processor.get_position_for_device(device, sessionid)
                else: 
                    data = self.data_processor.get_measurand_for_session(device, field ,sessionid)
            if data:
                return jsonify(data)
            else:
                return jsonify({"error": "Missing data"}), 404  

        @self.app.route('/api/count/<session>/<field>', methods=['GET'])
        def get_field_counts_per_session(session, field):
            if field not in self.valid_fields:
                return jsonify({"error": "Invalid field"}), 400
            unique_devices = self.data_processor.get_field_count(session, field)
            if unique_devices:
                return jsonify(unique_devices)
            else:
                return jsonify({"error": "No average position data available for this session."}), 404

        @self.app.route('/api/devices/<session>', methods=['GET'])
        def get_devices_per_session(session):
            unique_devices = self.data_processor.get_unique_devices_per_session(session)
            if unique_devices:
                return jsonify(unique_devices)
            else:
                return jsonify({"error": "No average position data available for this session."}), 404

        @self.app.route('/api/avg/<sessionid>', methods=['GET'])
        def get_average_values(sessionid):
            average_position_data = self.measurand_calculator.calculate_average_position(sessionid)
            if average_position_data:
                return jsonify(average_position_data)
            else:
                return jsonify({"error": "No average position data available for this session."}), 404

        @self.app.route('/api/mode/<sessionid>', methods=['GET'])
        def get_most_frequent_position(sessionid):
            most_frequent_position = self.measurand_calculator.most_frequent_position(sessionid)
            if most_frequent_position:
                return jsonify({"most_frequent_position": most_frequent_position})
            else:
                return jsonify({"error": "No position data available for this session."}), 404

        @self.app.route('/api/sigma/<sessionid>/<reference_type>', methods=['GET'])
        def get_sigma(sessionid, reference_type):
            try:
                sigma_values = self.measurand_calculator.calculate_sigma(sessionid, reference_type)
                if sigma_values:
                    return jsonify(sigma_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route('/api/drms/<sessionid>/<reference_type>', methods=['GET'])
        def get_drms(sessionid, reference_type):
            try:
                drms_values = self.measurand_calculator.calculate_drms(sessionid, reference_type)
                if drms_values:
                    return jsonify(drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route('/api/2drms/<sessionid>/<reference_type>', methods=['GET'])
        def get_2drms(sessionid, reference_type):
            try:
                two_drms_values = self.measurand_calculator.calculate_2drms(sessionid, reference_type)
                if two_drms_values:
                    return jsonify(two_drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
                
        @self.app.route('/api/cep/<sessionid>/<reference_type>', methods=['GET'])
        def get_cep(sessionid, reference_type):
            try:
                cep_values = self.measurand_calculator.calculate_cep(sessionid, reference_type)
                if cep_values:
                    return jsonify(cep_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
