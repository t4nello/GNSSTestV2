from flask import Flask, jsonify, request, g

class Router:
    def __init__(self, postgres_manager):
        self.postgres_manager = postgres_manager

    def configure_routes(self, app):
        @app.route('/sessions', methods=['GET'])
        def get_sessions():
            unique_session_ids = self.postgres_manager.get_unique_session_ids()
            return jsonify({"sessions": unique_session_ids})

        @app.route('/devices', methods=['GET'])
        def get_devices():
            unique_devices = self.postgres_manager.get_unique_devices()
            return jsonify({"devices": unique_devices})
        
        @app.route('/latitude/<selected_session>', methods=['GET'])
        def get_latitude(selected_session):
            latitude = self.postgres_manager.get_selected_latitude(selected_session)
            return jsonify({"latitude": latitude})