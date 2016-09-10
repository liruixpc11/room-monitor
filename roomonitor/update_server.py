# coding=utf-8
import json

from twisted.internet import reactor
from twisted.internet.protocol import Factory, connectionDone, Protocol, BaseProtocol
from twisted.protocols.basic import LineReceiver
from utils import publish_message, update_sensor_status, should_alert


class UpdateServer(LineReceiver):
    def connectionLost(self, reason=connectionDone):
        Protocol.connectionLost(self, reason)
        publish_message("connection lost from {0}: {1}".format(self.transport.client, reason))

    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        publish_message("connection made from {0}".format(self.transport.client))

    def lineReceived(self, line):
        data = json.loads(line)
        entries = data['entries']
        alert = ''
        for entry in entries:
            sensor_id = entry['sensor_id']
            status = entry['status']
            humidity = entry.get('humidity', None)
            temperature = entry.get('temperature', None)
            update_sensor_status(sensor_id, status, humidity, temperature)
            if status != 'OK':
                alert += '传感器{0}状态异常：{1}\n'.format(sensor_id, status)
            elif should_alert(temperature, humidity):
                alert += '传感器{0}数据异常，温度为{1}，湿度为{2}\n'.format(sensor_id, temperature, humidity)
        if alert:
            publish_message(alert)
        self.sendLine(json.dumps({
            "code": 0,
            "message": "OK"
        }))


def main():
    factory = Factory()
    factory.protocol = UpdateServer
    reactor.listenTCP(9999, factory)
    reactor.run()


if __name__ == '__main__':
    main()
