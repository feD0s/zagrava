from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Strategy(Base):
    __tablename__ = "strategy"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String(250))
    windowSize = Column(Integer)
    buyStakeSize = Column(Integer)
    buyBp = Column(Integer)
    buyCooldown = Column(Integer)
    buyMaxContracts = Column(Integer)
    sellStakeSize = Column(Integer)
    sellBp = Column(Integer)
    sellCooldown = Column(Integer)
    sellMinContracts = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
