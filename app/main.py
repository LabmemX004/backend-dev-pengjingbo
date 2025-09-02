from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 1) Load environment variables from .env file
load_dotenv()

# 2) Now you can safely read them
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

import boto3
from botocore.client import Config
import uuid

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(signature_version="s3v4"),
    aws_access_key_id=AWS_ACCESS_KEY_ID,          # or rely on your profile/instance role
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,  # if using .env
)
#///////////////////////////////////////////////////////////////////////////////////////


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
    
@app.get("/upload_test")
def upload_test():
   
    s3.upload_file("c:\\Users\\JD\\Desktop\\image for test2.png", "myawsbucket-for-event-master-project", "event-master-project-image/image-for-test2.jpg")
    
    return {"ok": True}

@app.get("/test/downloading")
def download_file():
    # Ensure the download folder exists
    # download_folder = os.path.join(os.path.dirname(__file__), "download")
    # os.makedirs(download_folder, exist_ok=True)
    # local_path = os.path.join(download_folder, "image-for-test2.jpg")
    imageName = "image for test1.png"
    s3.download_file("myawsbucket-for-event-master-project", imageName, f"C:\\Users\\JD\\Desktop\\Event master backend\\download\\{imageName}")
    return {"ok": True}

