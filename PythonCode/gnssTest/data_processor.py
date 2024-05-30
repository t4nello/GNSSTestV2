import psycopg2
from flask import g

class DataProcessor:
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
                    query = "SELECT DISTINCT sessionid FROM mqtt_consumer ORDER BY sessionid ASC;"
                    cursor.execute(query)
                    session_ids = [row[0] for row in cursor.fetchall()]
                    return session_ids
        except psycopg2.Error as error:
            print("Error fetching unique session IDs:", error)
            return []

    def get_unique_devices(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT DISTINCT device FROM mqtt_consumer;"
                    cursor.execute(query)
                    devices = [row[0] for row in cursor.fetchall()]
                    return devices
        except psycopg2.Error as error:
            print("Error fetching unique devices:", error)
            return []

    def get_position_for_session(self, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT device, time, latitude, longitude FROM mqtt_consumer WHERE sessionid = %s;"
                    cursor.execute(query, (sessionid,))
                    data = [{"device": row[0], "time": row[1], "latitude": row[2], "longitude": row[3]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching latitude and longitude for session:", error)
            return []


    def get_position_for_device(self, device, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT time, latitude, longitude FROM mqtt_consumer WHERE device = %s AND sessionid = %s;"
                    cursor.execute(query, (device, sessionid))
                    data = [{"time": row[0], "latitude": row[1], "longitude": row[2]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching latitude and longitude for device:", error)
            return []


    def get_measurand_for_device(self, field, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT device, time, %s FROM mqtt_consumer WHERE sessionid = %s"
                    cursor.execute(query, (field, sessionid))
                    data = [{"device": row[0], "time": row[1], "measurand": row[2]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching measurand for session:", error)
            return []

     
    def get_measurand_for_session(self, device, field, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT time, %s FROM mqtt_consumer WHERE sessionid = %s AND device = %s"
                    cursor.execute(query, (field, sessionid, device))
                    data = [{"time": row[0], "measurand": row[1]} for row in cursor.fetchall()]
                    return data
        except psycopg2.Error as error:
            print("Error fetching measurand for device:", error)
            return []


    def get_unique_devices_per_session(self, sessionid):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT DISTINCT device FROM mqtt_consumer WHERE sessionid = %s"
                    cursor.execute(query, (sessionid,))
                    devices = [row[0] for row in cursor.fetchall()]
                    return devices
        except psycopg2.Error as error:
            print("Error fetching unique devices:", error)
            return []

    def get_field_counts(self, sessionid, field):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT device, COUNT(%s) FROM mqtt_consumer WHERE sessionid = %s GROUP BY device"
                    cursor.execute(query, (field, sessionid,))
                    devices_counts = [{"device": row[0], "measurement": row[1]} for row in cursor.fetchall()]
                    
                    query_total = "SELECT COUNT(%s) FROM mqtt_consumer WHERE sessionid = %s"
                    cursor.execute(query_total, (field, sessionid,))
                    total_count = cursor.fetchone()[0]
                    
                    if total_count == 0 : 
                        return None
                    else:
                        total_record = {"total": total_count}
                        devices_counts.append(total_record)
                        return devices_counts
        except psycopg2.Error as error:
            print("Error fetching field counts:", error)
            return []
    