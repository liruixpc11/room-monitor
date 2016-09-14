# coding=utf-8
import logging
from datetime import datetime, timedelta
from lrweixin import WeiXinClientFactory
from db import DbFactory, SensorStatus, SensorLog, Controller

import settings

FACTORY = WeiXinClientFactory(settings.WEIXIN_AGENT_ID)
TEST_MODE = settings.MODE == 'TEST'
DB_FACTORY = DbFactory(settings.DB_URL)
DB_FACTORY.init_schema()

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig()


def publish_message(message):
    if settings.GAUGE_URL:
        message += "\n详情请查看: " + settings.GAUGE_URL
    if TEST_MODE:
        print 'SEND WEIXIN:', '\n  '.join(message.split('\n'))
    else:
        client = FACTORY.create_by_corp(settings.WEIXIN_CORP_ID, settings.WEIXIN_SECRET)
        client.publish_message(message)


def update_sensor_status(controller_name, sensor_id, status, update_time, report_time, temperature=None, humidity=None):
    session = DB_FACTORY.create_session()
    try:
        record = session.query(SensorStatus).filter(SensorStatus.controller_name == controller_name,
                                                    SensorStatus.sensor_id == sensor_id).scalar()
        if not record:
            record = SensorStatus(
                controller_name=controller_name,
                sensor_id=sensor_id,
                status=status,
                update_time=update_time,
                report_time=report_time,
                temperature=temperature,
                humidity=humidity
            )
            session.add(record)
        else:
            record.report_time = report_time
            record.status = status
            record.update_time = update_time
            record.temperature = temperature
            record.humidity = humidity

        log = SensorLog(
            controller_name=controller_name,
            sensor_id=sensor_id,
            status=status,
            update_time=update_time,
            report_time=report_time,
            temperature=temperature,
            humidity=humidity
        )
        session.add(log)

        session.commit()
    finally:
        session.close()


def update_controller_status(controller_name, ip, status):
    active_time = datetime.now()
    session = DB_FACTORY.create_session()
    try:
        record = session.query(Controller).filter(Controller.name == controller_name).scalar()
        if not record:
            record = Controller(
                name=controller_name,
                ip=ip,
                status=status,
                last_active_time = active_time
            )
            session.add(record)
        else:
            record.ip = ip
            record.status = status
            record.last_active_time = active_time
        session.commit()
    finally:
        session.close()


def query_sensor_logs(last_id=None, limit=0):
    session = DB_FACTORY.create_session()
    try:
        query = session.query(SensorLog)
        if last_id:
            query = query.filter(SensorLog.id > last_id)
        else:
            query = query.filter(SensorLog.update_time >= (datetime.now() - timedelta(hours=12)).strftime(TIME_FORMAT))
        query = query.order_by(SensorLog.id)
        if limit:
            query = query.limit(limit)
        return query.all()
    finally:
        session.close()


def query_sensor_status():
    session = DB_FACTORY.create_session()
    try:
        return session.query(SensorStatus).order_by(SensorStatus.sensor_id).all()
    finally:
        session.close()


def update_active_time(controller_name, active_time):
    session = DB_FACTORY.create_session()
    try:
        record = session.query(Controller).filter(Controller.name == controller_name).scalar()
        record.last_active_time = active_time
        session.commit()
    finally:
        session.close()


def should_alert(temperature, humidity):
    return temperature > 30 or humidity > 80


def create_logger(name):
    return logging.getLogger(name)
