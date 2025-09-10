from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey,func
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import enum



load_dotenv()

db_username = os.getenv("db_username")
db_password = os.getenv("db_password")
db_hostname = os.getenv("db_hostname")
db_port = os.getenv("db_port")
db_database = os.getenv("db_database")

db_url = f"mysql+pymysql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_database}"

engine = create_engine(db_url)

Base = declarative_base()


#Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#//////////////////////////////////////////////////////////////////////////////#
class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    role_type = Column(String(50),unique=True) #@unique NormalUser, EventProvider, WebManager
#//////////////////////////////////////////////////////////////////////////////#
class User_roles(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)  #int # fk
    role_id = Column(Integer,ForeignKey("roles.id"), nullable=False)  #int # fk
#//////////////////////////////////////////////////////////////////////////////#
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_name = Column(String(100),unique=True,nullable=False) #@unique
    email = Column(String(100),unique=True,nullable=False) #@unique
    hashed_password = Column(String(500),nullable=False)
    salt = Column(String(500),nullable=False)
    
    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#//////////////////////////////////////////////////////////////////////////////#

class Events(Base):
    
    # type: str
    # title: str
    # provider: str
    # StartDateAndTime: datetime  # parses "2025-08-31T02:30:00.123Z"
    # lastingTime: float
    # location: str
    # image: str
    # description: str

    __tablename__ = "events"

    event_provider_id = Column(Integer,ForeignKey("users.id"), nullable=False)  #int # fk
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    event_type= Column(String(50))  #str
    event_title= Column(String(100))  #str
    event_provider_name= Column(String(100))  #str
    showed_event_provider_name= Column(String(100))  #str
    event_start_date_and_time= Column(DateTime(timezone=True)) #datetime # parses "2025-08-31T02:30:00.123Z"
    event_duration_in_minutes= Column(Float) #float # in minutes
    event_location= Column(String(500))  #str
    event_imageUrl= Column(String(1000))  #str
    event_description= Column(String(10000))  #str

    event_total_ticket_number= Column(Integer) #int
    event_remaining_ticket_number= Column(Integer) #int

    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#//////////////////////////////////////////////////////////////////////////////#

class Booking_ticket_action_info(Base):
    __tablename__ = "booking_ticket_action_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)  #int # fk
    event_id = Column(Integer,ForeignKey("events.id"), nullable=False)  #int # fk
    status = Column(String(50),nullable=False, default="Booked") #str  # Booked, Cancelled, Attended

    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)