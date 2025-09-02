from dotenv import load_dotenv
import os
import boto3
from botocore.client import Config
import uuid

# 1) Load environment variables from .env file
load_dotenv()

# 2) Now you can safely read them
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")



s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(signature_version="s3v4"),
    aws_access_key_id=AWS_ACCESS_KEY_ID,          # or rely on your profile/instance role
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,  # if using .env
)