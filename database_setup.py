from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin

Base = declarative_base()


class Volunteer(Base, UserMixin):
    __tablename__ = 'volunteer'
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    rollno=Column(String(10),nullable=False)
    email=Column(String(250),nullable=False)
    branch=Column(String(250),nullable=False)
    mobileno=Column(Integer,nullable=False)
    gender=Column(String(250),nullable=False)
    year=Column(Integer,nullable=False)
    pasword=Column(String(250),nullable=False)
    picture = Column(String(250), nullable = False, unique =True)

class Studentreg(Base):
    __tablename__="studentreg"
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    rollno=Column(String(10),nullable=False)
    email=Column(String(250),nullable=False)
    branch=Column(String(250),nullable=False)
    mobileno=Column(Integer,nullable=False)
    gender=Column(String(250),nullable=False)
    year=Column(Integer,nullable=False)
    pasword=Column(String(250),nullable=False)
    picture = Column(String(250), nullable = False, unique =True)

class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    venue = Column(String(250), nullable=False)
    imgloc = Column(String(250), nullable=False)
    date = Column(Date, nullable = False, unique = True)
    info = Column(String(250), nullable = False)
    vol_id = Column(Integer, ForeignKey('volunteer.id'))
    volunteer = relationship(Volunteer)

class Circular(Base):
    __tablename__ = "circular"
    id = Column(Integer, primary_key=True)
    name = Column(String(50),nullable=False)
    venue = Column(String(250), nullable=False)
    date = Column(Date, nullable = False)
    info = Column(String(250), nullable = False)
    link = Column(String(250), nullable = False)


engine = create_engine('sqlite:///sritnss.db')


Base.metadata.create_all(engine)