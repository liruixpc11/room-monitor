import settings
from lrweixin import WeiXinClientFactory

FACTORY = WeiXinClientFactory(settings.AGENT_ID)
TEST_MODE = settings.MODE == 'TEST'


def publish_message(message):
    if TEST_MODE:
        print 'SEND WEIXIN:', message
    else:
        client = FACTORY.create_by_corp(settings.CORP_ID, settings.SECRET)
        client.publish_message(message)


def update_sensor_status(sensor_id, status, temperature=None, humidity=None):
    print 'UPDATE:', sensor_id, status


def should_alert(temperature, humidity):
    return temperature > 30 or humidity > 80