from fastapi import FastAPI 
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from .routes import s3Test



app = FastAPI()

# Frontend dev origins you want to allow
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=False,        
    allow_methods=["*"],            
    allow_headers=["*"],            
)

class createEvent(BaseModel):
    type: str
    title: str
    provider: str
    StartDateAndTime: str
    lastingTime: float
    location: str
    image: str
    description: str
    eventDate: datetime  # parses "2025-08-31T02:30:00.123Z"

list_events = []


#////////////////////////////////////////////////////////////////////////////////////////
@app.post("/test_datetime")
def test_datetime(event: createEvent):

    list_events.append(event)

    print(list_events)

    return {"ok": True, "received": event,
        "type": event.type,
        "title":event.title,
        "provider": event.provider,
        "StartDateAndTime": event.StartDateAndTime,
        "lastingTime": event.lastingTime,
        "location": event.location,
        "image": event.image,
        "description": event.description,

        "year": event.eventDate.year,            # e.g. 2025
        "month": event.eventDate.month,          # 1..12
        "date": event.eventDate.day,             # day of the month
        "day": event.eventDate.strftime("%A"),   # Monday, Tuesday, etc.
        "time": event.eventDate.strftime("%H:%M:%S"),  # 24h time like "14:30:00"
        }

@app.get("/event_info")
def event_info():
    return {
        "count": len(list_events),
        "events": list_events
    }

@app.get("/event/{num}")
def print_event(num: int):
    if len(list_events) < (num+1) or num <= -1:
        return {"error": "Invalid event number, try again."}
    else:
        return (
            {"list_events[num]": list_events[num]}
        )
    
app.include_router(s3Test.router)




