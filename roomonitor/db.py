from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, ForeignKey, Boolean, create_engine, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()


class SensorLog(Base):
    __tablename__ = 'sensor_log'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    controller_name = Column(String(64), ForeignKey("controller.name"))
    sensor_id = Column(String(64))
    status = Column(String(32))
    update_time = Column(DateTime())
    report_time = Column(DateTime())
    temperature = Column(Float())
    humidity = Column(Float())

    controller = relationship("Controller")


CONNECTED = 'connected'
DISCONNECTED = 'disconnected'


class Controller(Base):
    __tablename__ = 'controller'

    name = Column(String(64), primary_key=True)
    ip = Column(String(32))
    status = Column(Enum(CONNECTED, DISCONNECTED), default=DISCONNECTED)
    last_active_time = Column(DateTime())


class SensorStatus(Base):
    __tablename__ = 'sensor_status'

    controller_name = Column(String(64), ForeignKey("controller.name"), primary_key=True)
    sensor_id = Column(String(64), primary_key=True)
    status = Column(String(32))
    update_time = Column(DateTime())
    report_time = Column(DateTime())
    temperature = Column(Float())
    humidity = Column(Float())

    controller = relationship("Controller")


class DbFactory:
    def __init__(self, connection_url='sqlite:///:memory:'):
        self.connection_url = connection_url
        self.engine = create_engine(connection_url)
        self.make_session = sessionmaker(bind=self.engine)

    def init_schema(self):
        Base.metadata.create_all(self.engine)

    def create_connection(self):
        return self.engine.connect()

    def create_session(self, **kwargs):
        return self.make_session(**kwargs)
