from pydantic import BaseModel
from fastapi import APIRouter
import smtplib, os

router = APIRouter()

sever = smtplib.SMTP('smtp.gmail.com', 587)
sever.starttls()
sever.login(os.getenv("emailSender"), os.getenv("emailPassword"))
#print(os.getenv("emailPassword"))

class SignUpData(BaseModel):
    username: str
    email: str
    passwordPlainText: str

class SignInData(BaseModel):
    email: str
    passwordPlainText: str

class EmailForVerificationCode(BaseModel):
    email: str

@router.post("/emailForVerificationCode")
def email_for_verification_code(email: EmailForVerificationCode):
    print(f"Sending verification code to {email.email}")
    reciverEmail = email.email
    subject = "Verification code from Student Event"
    body = "it is a test for sending email from fastapi backend"
    message = f"Subject: {subject}\n\n{body}"
    sever.sendmail(os.getenv("emailSender"), reciverEmail, message)
    return {"ok": "True"}