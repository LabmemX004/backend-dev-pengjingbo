from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Body
from ..config import s3
from ..config import S3_BUCKET



router = APIRouter()



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
@router.post("/test_datetime")
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

@router.post("/upload-url")
def get_upload_url(filename: str = Body(..., embed=True), content_type: str = Body("image/jpeg", embed=True)):
    """Generate a presigned upload URL for S3"""
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": filename,
            "ContentType": content_type
        },
        ExpiresIn=300  # valid 5 minutes
    )
    return {"url": url, "key": filename}

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




