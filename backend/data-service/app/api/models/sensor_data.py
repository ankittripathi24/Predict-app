from sqlalchemy import Column, Integer, Float, DateTime
from ...database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    
    class Config:
        orm_mode = True