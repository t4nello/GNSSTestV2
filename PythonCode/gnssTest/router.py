from flask import jsonify, request
from flask_sock import Sock
from session_manager import SessionManager
from algorithm import Algorithm
import json

class Router:
    def __init__(self, app, sockets, mqtt_manager, config_manager, data_processor, measurand_calculator, algorithm):
        self.app = app
        self.mqtt_manager = mqtt_manager
        self.session_manager = SessionManager(mqtt_manager, config_manager)
        self.data_processor = data_processor
        self.sockets = sockets 
        self.measurand_calculator = measurand_calculator(self.data_processor)
        self.algorithm = algorithm
        self.valid_fields = ["latitude", "longitude", "position", "speed", "satellites", "altitude"]
        self.setup_routes()
        self.setup_signal_handlers()

    client_list = []

    def send_connected_device(self, sender, **kwargs):
        connected_device = kwargs.get('device')
        self.send_message_to_websocket({"connected_device": connected_device})

    def send_disconnected_device(self, sender, **kwargs):
        disconnected_device = kwargs.get('device')
        self.send_message_to_websocket({"disconnected_device": disconnected_device})

    def send_operative_device(self, sender, **kwargs):
        connected_device = kwargs.get('device')
        self.send_message_to_websocket({"operative_device": connected_device})

    def send_faulted_device(self, sender, **kwargs):
        disconnected_device = kwargs.get('device')
        self.send_message_to_websocket({"faulted_device": disconnected_device})

    def send_message_to_websocket(self, message):
        for client in self.sockets.clients:
            client.send("ping")
            client.send(json.dumps(message))

    def setup_signal_handlers(self):
        self.mqtt_manager.device_connected.connect(self.send_connected_device)
        self.mqtt_manager.device_disconnected.connect(self.send_disconnected_device)
        self.algorithm.device_faulted.connect(self.send_faulted_device)  # Poprawka
        self.algorithm.device_operative.connect(self.send_operative_device)  # Poprawka
        
    
    def send_message_to_websocket(self, message):
        clients = self.client_list.copy()
        for client in clients:
            try:
                client.send(json.dumps(message))
            except:
                clients.remove(client)

    def setup_routes(self):
        @self.sockets.route('/api/connected_devices', websocket=True)
        def handle_websocket(ws):
            self.client_list.append(ws)
            while True:
                data = ws.receive()
                ws.send(data)
        
        @self.app.route('/api/device/detect', methods=['POST'])
        def detect_device():
            try:
                device = request.json.get('Connected device')
                self.mqtt_manager.detect_device(device)
                return jsonify({"message": "location request sent succesfully"}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route('/api/session/start', methods=['POST'])
        def start_session():
            result = self.session_manager.enable_session()
            if isinstance(result, int):
                return jsonify({"session_id": result}), 200
            else:
                return jsonify({"error": result}), 400

        @self.app.route('/api/session/stop', methods=['POST'])
        def stop_session():
            result = self.session_manager.disable_session()
            if result == True:
                return jsonify({"status": "Session stopped succesfully"}), 200
            else:
                return jsonify({"error": "Session already Stopped"}), 400

        @self.app.route('/api/session/status',  methods=['GET'])
        def get_session_status():
            status = self.session_manager.get_session_status()
            return jsonify({"Status": status}), 200

       
        @self.app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            unique_session_ids = self.data_processor.get_unique_session_ids()
            return jsonify({"sessions": unique_session_ids})


        @self.app.route('/api/devices', methods=['GET'])
        def get_devices():
            sessionid = request.args.get('session_id')
            if sessionid is not None:
                unique_devices = self.data_processor.get_unique_devices_per_session(sessionid)
            else:
                unique_devices = self.data_processor.get_unique_devices()
            if len(unique_devices) > 0: 
                return jsonify({"devices": unique_devices}), 200
            else:
                return jsonify({"error": "No data available for this session"}), 404  

        @self.app.route('/api/session/data', methods=['GET'])
        def get_data():
            sessionid = request.args.get('session_id')
            device = request.args.get('device')
            field = request.args.get('field')
            if not sessionid or not device or not field:
                return jsonify({"error": "Missing parameter"}), 400
            else:  
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

        @self.app.route('/api/session/field-count', methods=['GET'])
        def get_field_counts_per_session():
            sessionid = request.args.get('session_id')
            field = request.args.get('field')
            if not sessionid or not field:
                return jsonify({"error": "Missing parameter"}), 400
            else:  
                if field not in self.valid_fields:
                    return jsonify({"error": "Invalid field"}), 400
                unique_devices = self.data_processor.get_field_count(sessionid, field)
                if unique_devices:
                    return jsonify(unique_devices)
                else:
                    return jsonify({"error": "No average position data available for this session."}), 404

        @self.app.route('/api/average', methods=['GET'])
        def get_average_values():
            sessionid = request.args.get('session_id')
            if not sessionid:
                return jsonify({"error": "Missing parameter"}), 400
            else:  
                average_position_data = self.measurand_calculator.calculate_average_position(sessionid)
                if average_position_data:
                    return jsonify(average_position_data)
                else:
                    return jsonify({"error": "No average position data available for this session."}), 404

        @self.app.route('/api/mode', methods=['GET'])
        def get_most_frequent_position():
            sessionid = request.args.get('session_id')
            if not sessionid:
                return jsonify({"error": "Missing parameter"}), 400
            else:  
                most_frequent_position = self.measurand_calculator.most_frequent_position(sessionid)
                if most_frequent_position:
                    return jsonify({"most_frequent_position": most_frequent_position})
                else:
                    return jsonify({"error": "No position data available for this session."}), 404

        @self.app.route('/api/sigma', methods=['GET'])
        def get_sigma():
            sessionid = request.args.get('session_id')
            reference_type = request.args.get('reference_type')
            if not sessionid or not reference_type:
                return jsonify({"error": "Missing parameter"}), 400
            else:  
                try:
                    sigma_values = self.measurand_calculator.calculate_sigma(sessionid, reference_type)
                    if sigma_values:
                        return jsonify(sigma_values)
                    else:
                        return jsonify({"error": "No position data available for this session."}), 404
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400

        @self.app.route('/api/drms', methods=['GET'])
        def get_drms():
            sessionid = request.args.get('session_id')
            reference_type = request.args.get('reference_type')
            if not sessionid or not reference_type:
                return jsonify({"error": "Missing parameter"}), 400
            try:
                drms_values = self.measurand_calculator.calculate_drms(sessionid, reference_type)
                if drms_values:
                    return jsonify(drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route('/api/2drms', methods=['GET'])
        def get_2drms():
            sessionid = request.args.get('session_id')
            reference_type = request.args.get('reference_type')
            if not sessionid or not reference_type:
                return jsonify({"error": "Missing parameter"}), 400
            try:
                drms_values = self.measurand_calculator.calculate_2drms(sessionid, reference_type)
                if drms_values:
                    return jsonify(drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
                
        @self.app.route('/api/cep', methods=['GET'])
        def get_cep():
            sessionid = request.args.get('session_id')
            reference_type = request.args.get('reference_type')
            if not sessionid or not reference_type:
                return jsonify({"error": "Missing parameter"}), 400
            try:
                drms_values = self.measurand_calculator.calculate_cep(sessionid, reference_type)
                if drms_values:
                    return jsonify(drms_values)
                else:
                    return jsonify({"error": "No position data available for this session."}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
        @self.app.route('/api/alghoritm/threshold/set', methods=['POST'])
        def get_threshold():
            try:
                threshold = request.json.get('threshold')
                self.algorithm.on_threshold_received(threshold)
                return jsonify({"message": "Threshold set successfully", "threshold": threshold}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
