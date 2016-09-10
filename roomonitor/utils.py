import logging
from datetime import datetime
from lrweixin import WeiXinClientFactory
from db import DbFactory, SensorStatus

import settings

FACTORY = WeiXinClientFactory(settings.WEIXIN_AGENT_ID)
TEST_MODE = settings.MODE == 'TEST'
DB_FACTORY = DbFactory(settings.DB_URL)
DB_FACTORY.init_schema()

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig()


def publish_message(message):
    if TEST_MODE:
        print 'SEND WEIXIN:', message
    else:
        client = FACTORY.create_by_corp(settings.WEIXIN_CORP_ID, settings.WEIXIN_SECRET)
        client.publish_message(message)


def update_sensor_status(sensor_id, status, update_time, temperature=None, humidity=None):
    session = DB_FACTORY.create_session()
    try:
        record = session.query(SensorStatus).filter(SensorStatus.sensor_id == sensor_id).scalar()
        if not record:
            record = SensorStatus(
                sensor_id=sensor_id,
                status=status,
                update_time=update_time,
                temperature=temperature,
                humidity=humidity
            )
            session.add(record)
        else:
            record.status = status
            record.update_time = update_time
            record.temperature = temperature
            record.humidity = humidity
        session.commit()
    finally:
        session.close()

def should_alert(temperature, humidity):
    return temperature > 30 or humidity > 80


def create_logger(name):
    return logging.getLogger(name)
