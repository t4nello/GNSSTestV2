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

    def execute_query(self, query, params=None):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return cursor.fetchall()
        except psycopg2.Error as error:
            print("Error executing query:", error)
            return []

    def get_unique_session_ids(self):
        query = "SELECT DISTINCT sessionid FROM mqtt_consumer ORDER BY sessionid ASC;"
        return [row[0] for row in self.execute_query(query)]

    def get_unique_devices(self):
        query = "SELECT DISTINCT device FROM mqtt_consumer;"
        return [row[0] for row in self.execute_query(query)]

    def get_position_for_session(self, sessionid):
        query = "SELECT device, time, latitude, longitude FROM mqtt_consumer WHERE sessionid = %s;"
        return [{"device": row[0], "time": row[1], "latitude": row[2], "longitude": row[3]} for row in self.execute_query(query, (sessionid,))]

    def get_position_for_device(self, device, sessionid):
        query = "SELECT time, latitude, longitude FROM mqtt_consumer WHERE device = %s AND sessionid = %s;"
        return [{"time": row[0], "latitude": row[1], "longitude": row[2]} for row in self.execute_query(query, (device, sessionid))]

    def get_measurand_for_device(self, field, sessionid):
        query = "SELECT device, time, %s FROM mqtt_consumer WHERE sessionid = %s;"
        return [{"device": row[0], "time": row[1], "measurand": row[2]} for row in self.execute_query(query, (field, sessionid))]

    def get_measurand_for_session(self, device, field, sessionid):
        query = "SELECT time, %s FROM mqtt_consumer WHERE sessionid = %s AND device = %s;"
        return [{"time": row[0], "measurand": row[1]} for row in self.execute_query(query, (field, sessionid, device))]

    def get_unique_devices_per_session(self, sessionid):
        query = "SELECT DISTINCT device FROM mqtt_consumer WHERE sessionid = %s;"
        return [row[0] for row in self.execute_query(query, (sessionid,))]

    def get_field_count(self, sessionid, field):
        query = "SELECT device, COUNT(%s) FROM mqtt_consumer WHERE sessionid = %s GROUP BY device;"
        devices_counts = [{"device": row[0], "measurement": row[1]} for row in self.execute_query(query, (field, sessionid))]

        query_total = "SELECT COUNT(%s) FROM mqtt_consumer WHERE sessionid = %s;"
        total_count = self.execute_query(query_total, (field, sessionid,))[0][0]

        if total_count == 0:
            return None
        else:
            total_record = {"total": total_count}
            devices_counts.append(total_record)
            return devices_counts
