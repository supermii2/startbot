#A class that handles server data

class ServerDataHandler():
    def __init__(self):
        self.data = {}

    def write_data(self, server_id: int, key: str, value):
        if server_id not in self.data:
            self.data[server_id] = {}
        self.data[server_id][key] = value

    def read_data(self, server_id, key):
        if server_id not in self.data:
            return None
        
        if key not in self.data[server_id]:
            return None
        
        return self.data[server_id][key]