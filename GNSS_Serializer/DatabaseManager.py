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
    
    def get_position_for_session(self, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT device, time, latitude, longitude FROM mqtt_consumer WHERE sessionid = %s", (sessionid,))
                    data = [{"device": row[0], "time": row[1], "latitude": row[2], "longitude": row[3]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching latitude and longitude for session:", error)
            return []

    def get_position_for_device(self, device, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT time, latitude, longitude FROM mqtt_consumer WHERE device = %s AND sessionid = %s", (device, sessionid))
                    data = [{"time": row[0], "latitude": row[1], "longitude": row[2]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching latitude and longitude for device:", error)
            return []

    def get_measurand_for_device(self, field, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT device, time, {} FROM mqtt_consumer WHERE sessionid = %s".format(field)
                    cursor.execute(query, (sessionid,))
                    data = [{"device": row[0], "time": row[1], "measurand": row[2]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching measurand for session:", error)
            return []
     
    def get_measurand_for_session(self, device, field, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT time, {} FROM mqtt_consumer WHERE sessionid = %s AND device = %s".format(field)
                    cursor.execute(query, (sessionid, device))
                    data = [{"time": row[0], "measurand": row[1]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching measurand for device:", error)
            return []

    def get_unique_devices_per_session(self, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT device FROM mqtt_consumer WHERE sessionid = %s", (sessionid,))
                    devices = [row[0] for row in cursor.fetchall()]
                    return devices
        except psycopg2.Error as error:
            print("Error fetching unique devices:", error)
            return []
