from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///flats_async.db')

Base = declarative_base()

LocalSession = sessionmaker(bind=engine)


class Flat(Base):
    __tablename__ = 'flats'
    id = Column(Integer, primary_key=True)
    img_link = Column(String(150))
    title = Column(String(150))
    date = Column(String(50))
    city = Column(String(150))
    beds = Column(String(150))
    description = Column(Text())
    currency = Column(String(150))
    price = Column(String(150))


Base.metadata.create_all(engine)
