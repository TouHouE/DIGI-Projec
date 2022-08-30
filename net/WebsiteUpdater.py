import json
import re
import websocket
__all__ = ['WebsiteUpdater']
DEFAULT_IP = '192.168.0.10'
DEFAULT_IP = 9001


class WebsiteUpdater:
    def __init__(self, ip: str = DEFAULT_IP, port: int = DEFAULT_IP):
        self.ip = ip
        self.port = port

    def send(self, data):
        ws = websocket.create_connection(f"ws://{self.ip}:{self.port}")
        ws.send(data)

    def set_ip(self, ip: str):
        if re.search("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip):
            self.ip = ip



    def set_port(self, port: int):
        self.port = port
