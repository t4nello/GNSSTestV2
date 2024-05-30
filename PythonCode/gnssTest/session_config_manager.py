import json

class SessionConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                data = file.read()
                if not data:
                    default_config = {
                        "sessionId": 0,
                        "status": "stopped",
                    }
                    self.save_config(default_config)
                    return default_config
                else:
                    return json.loads(data)
        except FileNotFoundError:
            default_config = {
                "sessionId": 0,
                "status": "stopped",
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config_data):
        with open(self.config_file, 'w') as file:
            json.dump(config_data, file)
