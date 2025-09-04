from datetime import datetime
from dbConnection import Base
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey,func
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_name = Column(String) #@unique
    email = Column(String) #@unique
    password = Column(String)
    
    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#//////////////////////////////////////////////////////////////////////////////#

class Event_providers(Base):
    __tablename__ = "event_providers"

    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)  #int # fk

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

    event_provider_id = Column(Integer,ForeignKey("event_providers.id"), nullable=False)  #int # fk
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    event_type= Column(String)  #str
    event_title= Column(String)  #str
    event_provider_name= Column(String)  #str
    event_start_date_and_time= Column(DateTime(timezone=True)) #datetime # parses "2025-08-31T02:30:00.123Z"
    event_lasting_time= Column(float) #float # in minutes
    event_location= Column(String)  #str
    event_imageUrl= Column(String)  #str
    event_description= Column(String)  #str

    event_total_ticket_number= Column(Integer) #int
    event_remaining_ticket_number= Column(Integer) #int

    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#//////////////////////////////////////////////////////////////////////////////#

class Join_events_info(Base):
    __tablename__ = "join_events_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True) #int #@unique pk
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)  #int # fk
    event_id = Column(Integer,ForeignKey("events.id"), nullable=False)  #int # fk

    #optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)