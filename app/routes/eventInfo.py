from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Body,HTTPException, Query, Depends

from app.auth.jwt_bearer import get_current_user, jwtBearer
from ..config import s3
from ..config import S3_BUCKET
import time, os, uuid
from ..blueprint.dbBlueprint import SessionLocal, Events, Users
from sqlalchemy.orm import Session




router = APIRouter()



class createEvent(BaseModel):
    user_id: int
    type: str
    title: str
    provider: str
    StartDateAndTime: datetime  # parses "2025-08-31T02:30:00.123Z"
    lastingTime: float
    location: str
    image: str
    description: str
    totalTicketNumber: int

list_events = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/test_datetime",dependencies=[Depends(jwtBearer())])
def test_datetime(event: createEvent,db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):

    if(int(current_user["user_id"]) != event.user_id):
        raise HTTPException(status_code=403, detail="User ID does not match the token")
    if(current_user["roles"].count("EventProvider") == 0):
        raise HTTPException(status_code=403, detail="User is not an event provider")
    

    print("Received event:", event)

    db_event = Events(
        event_provider_id=event.user_id,  #int # fk
        event_type=event.type,
        event_title=event.title,
        event_provider_name=event.provider,
        showed_event_provider_name=event.provider,
        event_start_date_and_time=event.StartDateAndTime,
        event_duration_in_minutes=event.lastingTime,
        event_location=event.location,
        event_imageUrl=event.image,
        event_description=event.description,
        event_total_ticket_number=event.totalTicketNumber,
        event_remaining_ticket_number=event.totalTicketNumber,
        
    )

    db.add(db_event)
    db.commit()
    

    return {"ok": True, "received": event,
        "type": event.type,
        "title":event.title,
        "provider": event.provider,
        "StartDateAndTime": event.StartDateAndTime,
        "lastingTime": event.lastingTime,
        "location": event.location,
        "image": event.image,
        "description": event.description,

        "year": event.StartDateAndTime.year,            # e.g. 2025
        "month": event.StartDateAndTime.month,          # 1..12
        "date": event.StartDateAndTime.day,             # day of the month
        "day": event.StartDateAndTime.strftime("%A"),   # Monday, Tuesday, etc.
        "time": event.StartDateAndTime.strftime("%H:%M:%S"),  # 24h time like "14:30:00"
        }

@router.get("/event_info")
def event_info():
    return {
        "count": len(list_events),
        "events": list_events
    }

@router.get("/event/{num}")
def print_event(num: int):
    if len(list_events) < (num+1) or num <= -1:
        return {"error": "Invalid event number, try again."}
    else:
        return (
            {"list_events[num]": list_events[num]}
        )
    

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    
    content = await file.read()

    save_path = f"C:\\Users\\JD\\Desktop\\Event master backend\\download\\"

    with open(f"{save_path}{file.filename}", "wb") as fN:
        fN.write(content)
    

    return {"ok": "test passed", "filename": file.filename}


@router.post("/upload-url",dependencies=[Depends(jwtBearer())])
def get_upload_form(
    filename: str = Body(...),
    content_type: str = Body(...),
    current_user: dict = Depends(get_current_user),
    ):
    
    if(current_user["roles"].count("EventProvider") == 0):
        print("User is not an event provider from upload-url")
        raise HTTPException(status_code=403, detail="User is not an event provider")

    print("filename:", filename)
    print("content_type:", content_type)
    folder = "event-master-project-image"
    unique_name = f"{folder}/{time.strftime('%Y/%m/%d')}{uuid.uuid4().hex}{content_type}"
    print("unique_name:", unique_name)
    # return(filename, content_type)
    presign = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=unique_name,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}],
        ExpiresIn=300,
    )
    return presign  # {"url": "...", "fields": {...}}





@router.get("/download-url/{filename}")
def get_download_url(filename: str):
    """Generate a presigned download URL for a file in S3."""
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": filename,
        },
        ExpiresIn=300  # URL valid for 5 minutes
    )
    return {"url": url}


@router.get("/images/url")
def get_presigned_url(key: str = Query(...), ttl: int = 3600):
    try:
        ttl = max(10, min(ttl, 7*24*3600))
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": key},
            ExpiresIn=ttl,
        )
        return {"url": url, "expiresAt": int(time.time()) + ttl}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/a_page_of_events")
def a_page_of_events(db: Session = Depends(get_db)):
    events = db.query(Events).order_by(Events.event_start_date_and_time.desc()).limit(100).all()
    return events

