from pydantic import BaseModel
from fastapi import APIRouter
import smtplib, os, hashlib, random
import redis

router = APIRouter()

sever = smtplib.SMTP('smtp.gmail.com', 587)
sever.starttls()
sever.login(os.getenv("emailSender"), os.getenv("emailPassword"))
#print(os.getenv("emailPassword"))

r = redis.Redis(host=os.getenv("redisURL"), port=int(os.getenv("redisPort")),db=0, decode_responses=True)

class SignUpData(BaseModel):
    username: str
    email: str
    passwordPlainText: str
    verificationCode: str

class SignInData(BaseModel):
    email: str
    passwordPlainText: str

class EmailForVerificationCode(BaseModel):
    email: str

@router.post("/emailForVerificationCode")
def email_for_verification_code(email: EmailForVerificationCode):
    print(f"Sending verification code to {email.email}")
    reciverEmail = email.email
    # Generate a verification code
    verification_code = str(random.randint(100000, 999999))
    verification_code_hashed = hashlib.sha256(verification_code.encode()).hexdigest()
    #print(F"origin:{verification_code}")
    print(F"hashed:{verification_code_hashed}")
    print(f"Generated verification code: {verification_code}")
    r.setex(reciverEmail, 600, verification_code_hashed)
    print(f"itshould be here:{r.get(reciverEmail)}")
    # Store the verification code in Redis with an expiration time (e.g., 10 minutes)
    subject = "Verification code from Student Event"
    body = "your 6-digit verification code is: " + verification_code + ". It is valid for 10 minutes. If you did not request this code, please ignore this email."
    message = f"Subject: {subject}\n\n{body}"
    try:
        sever.sendmail(os.getenv("emailSender"), reciverEmail, message)
    except:
        return {"ok": "False"}
    return {"ok": "True"}

@router.post("/signUp")
def sign_up(data: SignUpData):
    print(f"Signing up user: {data.username}, email: {data.email}")
    # Verify the code
    if(hashlib.sha256(data.verificationCode.encode()).hexdigest() != r.get(data.email)):
        print("Verification code is incorrect.")
        return {"status": "incorrectVerificationCode"}
    else:
        print("Verification code is correct.")
        return {"status": "SuccessfullySignedUp"}