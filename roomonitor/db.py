from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, ForeignKey, Boolean, create_engine, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class SensorStatus(Base):
    __tablename__ = 'sensor_status'

    sensor_id = Column(String(64), primary_key=True)
    status = Column(String(32))
    update_time = Column(DateTime())
    temperature = Column(Float())
    humidity = Column(Float())


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
