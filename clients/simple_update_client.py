import socket
import json

s = socket.socket()
s.connect(('127.0.0.1', 9999))
s.sendall(json.dumps({
    'entries': [
        {
            'sensor_id': '1',
            'status': 'OK',
            'humidity': 72,
            'temperature': 26
        },
        {
            'sensor_id': '2',
            'status': 'OK',
            'humidity': 84,
            'temperature': 27
        },
        {
            'sensor_id': '3',
            'status': 'DOWN',
        }
    ]
}) + "\r\n")
print s.recv(1024)
s.close()
