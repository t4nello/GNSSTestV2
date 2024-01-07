# config_manager.py

import json

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                data = file.read()
                if not data:
                    default_config = {
                        "session_number": 1233,
                        "session_status": "stopped",
                    }
                    with open(self.config_file, 'w') as new_file:
                        json.dump(default_config, new_file)
                    return default_config
                else:
                    return json.loads(data)
        except FileNotFoundError:
            default_config = {
                "session_number": 1,
                "session_status": "stopped",
            }
            with open(self.config_file, 'w') as new_file:
                json.dump(default_config, new_file)
            return default_config

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file)
