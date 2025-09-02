from ..config import s3
from ..config import S3_BUCKET
from fastapi import APIRouter

router = APIRouter()


@router.get("/upload_test")
def upload_test():
   
    s3.upload_file("c:\\Users\\JD\\Desktop\\image for test2.png", "myawsbucket-for-event-master-project", "event-master-project-image/image-for-test2.jpg")
    
    return {"ok": True}

@router.get("/test/downloading")
def download_file():
    imageName = "image for test1.png"
    s3.download_file("myawsbucket-for-event-master-project", imageName, f"C:\\Users\\JD\\Desktop\\Event master backend\\download\\{imageName}")
    return {"ok": True}