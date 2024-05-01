import psycopg2
from flask import Flask, jsonify, g
class PostgresDBManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def get_connection(self):
        if 'db' not in g:
            g.db = psycopg2.connect(self.connection_string)
        return g.db

    def disconnect(self):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def get_unique_session_ids(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT sessionid FROM mqtt_consumer ORDER BY sessionid DESC;")
                    session_ids = [row[0] for row in cursor.fetchall()]
                    return session_ids
        except psycopg2.Error as error:
            print("Error fetching unique session IDs:", error)
            return []

    def get_unique_devices(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT device FROM mqtt_consumer;")
                    devices = [row[0] for row in cursor.fetchall()]
                    return devices
        except psycopg2.Error as error:
            print("Error fetching unique devices:", error)
            return []


    def get_selected_latitude(self, selected_session):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT time, device, latitude FROM mqtt_consumer WHERE sessionid = %s", (selected_session,))
                    latitude = cursor.fetchall()
                    return latitude
        except psycopg2.Error as error:
            print("Error fetching latitude:", error)
            return []