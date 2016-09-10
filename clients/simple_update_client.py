# coding=utf-8
import socket
import json
from datetime import datetime

s = socket.socket()
s.connect(('127.0.0.1', 9999))
s.sendall(json.dumps({
    'type': 'login',
    'info': {
        'name': '测试用传感器',
        'secret': 'secret'
    }
}) + "\r\n")
print s.recv(1024)
s.sendall(json.dumps({
    'type': 'data',
    'entries': [
        {
            'sensor_id': '1',
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'OK',
            'humidity': 72,
            'temperature': 26
        },
        {
            'sensor_id': '2',
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'OK',
            'humidity': 84,
            'temperature': 27
        },
        {
            'sensor_id': '3',
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'DOWN',
        }
    ]
}) + "\r\n")
print s.recv(1024)
s.close()
