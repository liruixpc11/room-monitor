# coding=utf-8
import json
from datetime import datetime

from twisted.internet import reactor
from twisted.internet.protocol import Factory, connectionDone, Protocol, BaseProtocol
from twisted.protocols.basic import LineReceiver
from utils import publish_message, update_sensor_status, should_alert, TIME_FORMAT, create_logger

import settings


LOG = create_logger(__name__)
ERRORS = [
    'OK',
    'LOGIN_FAILED',
    'NOT_LOGIN',
    'UNKNOWN_TYPE',
    'INTERNAL_ERROR'
]
LOGIN_FAILED = 1
NOT_LOGIN = 2
UNKNOWN_TYPE = 3
INTERNAL_ERROR = 4


class UpdateServer(LineReceiver):
    def __init__(self):
        self.login_pass = False
        self.client_name = ''

    def connectionLost(self, reason=connectionDone):
        Protocol.connectionLost(self, reason)
        LOG.warn("{0} connection lost because of {1}".format(self.client_desc(), reason))
        if self.login_pass:
            publish_message("警告：\n客户端{0}断开连接".format(self.client_desc()))

    def connectionMade(self):
        BaseProtocol.connectionMade(self)
        LOG.info("{0} connection made".format(self.client_desc()))

    def client_desc(self):
        return '[{0}{1}]'.format(self.client_name.encode('utf-8'), self.transport.client)

    def lineReceived(self, line):
        try:
            self.handle_line(line)
        except Exception as ex:
            LOG.exception(ex)
            self.reply(INTERNAL_ERROR, ex.message)

    def handle_line(self, line):
        data = json.loads(line)
        type_ = data['type']
        if type_ == 'login':
            LOG.debug("LOGIN message")
            self.on_login(data['info'])
        else:
            if not self.login_pass:
                self.reply(NOT_LOGIN)
                LOG.warn("{0} not login".format(self.client_desc()))
                return

            if type_ == 'data':
                LOG.debug("DATA message")
                self.on_data(data)
            else:
                LOG.warn("UNKNOWN message")
                self.reply(UNKNOWN_TYPE)

    def on_login(self, login_info):
        self.client_name = login_info['name']
        secret = login_info['secret']
        if secret == settings.SECRET:
            self.login_pass = True
            self.reply()
        else:
            LOG.warn("{0} login failed".format(self.client_desc()))
            self.reply(LOGIN_FAILED)

    def on_data(self, data):
        entries = data['entries']
        alert = []
        for entry in entries:
            sensor_id = entry['sensor_id']
            status = entry['status']
            update_time = entry['update_time']
            update_time = datetime.strptime(update_time, TIME_FORMAT)
            humidity = entry.get('humidity', None)
            temperature = entry.get('temperature', None)
            update_sensor_status(sensor_id, status, update_time, humidity, temperature)
            if status != 'OK':
                alert.append('[传感器{0}]状态异常，当前状态为"{1}"'.format(sensor_id, status))
            elif should_alert(temperature, humidity):
                alert.append('[传感器{0}]数据异常，温度为{1}，湿度为{2}'.format(sensor_id, temperature, humidity))
        if alert:
            publish_message('警告：\n' + '；\n'.join(alert) + "。")
        self.reply()

    def reply(self, code=0, message=None):
        self.sendLine(json.dumps({
            'code': code,
            'message': message if message else ERRORS[code]
        }))


def main():
    factory = Factory()
    factory.protocol = UpdateServer
    reactor.listenTCP(9999, factory)
    reactor.run()


if __name__ == '__main__':
    main()
