import json
import socket
import threading
import Queue
import logging
import time
import random
import get_tem
from datetime import datetime
from settings import MODE

logging.basicConfig()
LOG = logging.getLogger(__name__)


class ServerException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __unicode__(self):
        return u'[{0}]: {1}'.format(self.code, self.message)

    def __str__(self):
        return unicode(self).encode("utf-8")


class ReportThread(threading.Thread):
    '''
    to report to server
    '''

    def __init__(self, action_queue, server_address, secret, controller_name):
        super(ReportThread, self).__init__()
        self.action_queue = action_queue
        self.daemon = True
        self.connection = None
        self.server_address = server_address
        self.secret = secret
        self.controller_name = controller_name
        self.buffer = ''

    def run(self):
        self.connect()
        while 1:
            action = self.action_queue.get()
            if not action:
                self.disconnect()
                return

            done = False
            while not done:
                try:
                    self.process_action(action)
                    done = True
                except ServerException as ex:
                    LOG.warn("process action failure from server: {0}".format(ex))
                except Exception as ex:
                    LOG.warn("process action failed, will retry; [{0}] : {1}".format(action, ex))
                    LOG.exception(ex)
                finally:
                    time.sleep(5)

    def process_action(self, action):
        action_name, action_args = action
        if action_name == 'heartbeat':
            self.send_message({
                'type': 'heartbeat'
            })
            self.check_reply()
        elif action_name == 'report':
            self.send_message({
                'type': 'data',
                'entries': action_args
            })
            self.check_reply()
        else:
            LOG.warning('unknown action type: ' + action_name)

    def send_message(self, message):
        has_sent = False
        while not has_sent:
            try:
                self.connection.sendall(json.dumps(message) + '\r\n')
                has_sent = True
            except IOError:
                self.connect()

    def connect(self):
        self.disconnect()
        done = False
        while not done:
            try:
                self.connection = socket.socket()
                self.connection.connect(self.server_address)
                self.login()
                done = True
            except Exception, ex:
                time.sleep(5)
                LOG.error("connect failed: " + str(ex))
                self.disconnect()

    def receive_reply(self):
        while not '\r\n' in self.buffer:
            self.buffer += self.connection.recv(1024)
            if '\r\n' in self.buffer:
                index = self.buffer.index('\r\n')
                reply_string = self.buffer[0:index]
                self.buffer = self.buffer[index + 2:]
                return json.loads(reply_string)

    def check_reply(self):
        reply = self.receive_reply()
        if reply['code'] > 0:
            raise ServerException(reply['code'], reply['message'])

    def login(self):
        self.send_message({
            'type': 'login',
            'info': {
                'name': self.controller_name,
                'secret': self.secret
            }
        })
        self.check_reply()

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None


class HeartbeatThread(threading.Thread):
    '''
    to generate heartbeat action
    '''

    def __init__(self, action_queue, interval_seconds=60):
        super(HeartbeatThread, self).__init__()
        self.action_queue = action_queue
        self.daemon = True
        self.interval_seconds = interval_seconds

    def run(self):
        while 1:
            time.sleep(self.interval_seconds)
            self.action_queue.put(('heartbeat', None))


class SensorControlThread(threading.Thread):
    '''
    to trigger sensor action
    '''

    def __init__(self, action_queue):
        super(SensorControlThread, self).__init__()
        self.action_queue = action_queue
        self.daemon = True

    def run(self):
        while 1:
            time.sleep(5)
            try:
                result = self.sense()
                if result and len(result):
                    self.action_queue.put(('report', result))
                else:
                    LOG.info("sensor nothing")
            except Exception, ex:
                LOG.warn("sense error: " + str(ex))

    def sense(self):
        pins = [15, 18]

        result = []
        for i, pin in enumerate(pins):
            temperature, humility = get_tem.sense_th(pin)
            if temperature > -255:
                result.append({
                    'sensor_id': str(i + 1),
                    'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'OK',
                    'humidity': humility,
                    'temperature': temperature
                })

        return result


def main():
    LOG.info('initializing')
    action_queue = Queue.Queue(1024)
    report_thread = ReportThread(action_queue, ('115.28.100.161', 9999), 'secret', MODE)
    report_thread.start()

    HeartbeatThread(action_queue).start()
    SensorControlThread(action_queue).start()

    LOG.info("running")
    report_thread.join()


if __name__ == '__main__':
    main()
