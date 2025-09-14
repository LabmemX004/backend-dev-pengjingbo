from urllib import response
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, Depends, Request, Response
import smtplib, os, hashlib, random
import redis
from sqlalchemy.orm import Session
from ..blueprint.dbBlueprint import SessionLocal, Users, Roles, User_roles
import bcrypt
from ..auth.jwt import ACCESS_TTL, REFRESH_TTL, create_access_token, create_refresh_token, verify_refresh

router = APIRouter()

sever = smtplib.SMTP('smtp.gmail.com', 587)
sever.starttls()
sever.login(os.getenv("emailSender"), os.getenv("emailPassword"))
#print(os.getenv("emailPassword"))

r = redis.Redis(host=os.getenv("redisURL"), port=int(os.getenv("redisPort")),db=0, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
def sign_up(data: SignUpData, db: Session = Depends(get_db)):
    print(f"Signing up user: {data.username}, email: {data.email}")
    # Verify the code
    if(hashlib.sha256(data.verificationCode.encode()).hexdigest() != r.get(data.email)):
        print("Verification code is incorrect.")
        return {"status": "incorrectVerificationCode"}
    else:
        # Hash the password
        hashed_password = bcrypt.hashpw(data.passwordPlainText.encode('utf-8'), bcrypt.gensalt())
        # Create a new user
        new_user = Users(
            user_name=data.username,
            email=data.email,
            hashed_password=hashed_password.decode('utf-8')
        )
        if(db.query(Users).filter(Users.email == data.email).first() != None):
            print("Email already exists.")
            return {"status": "emailAlreadyExists"}
        if(db.query(Users).filter(Users.user_name == data.username).first() != None):
            print("Username already exists.")
            return {"status": "usernameAlreadyExists"}
        try:
            db.add(new_user)
            db.commit()
        except Exception as e:
            print(f"Error during sign up: {e}")
            return {"status": "signUpFailed"}
        
        db.refresh(new_user)
        new_user_role = User_roles(
            user_id=db.query(Users).filter(Users.email == data.email).first().id,
            role_id=1 # default: NormalUser
        )
        try:
            db.add(new_user_role)
            db.commit()
        except Exception as e:
            print(f"Error assigning role during sign up: {e}")
            return {"status": "signUpFailed"}
        print("Verification code is correct.")
        return {"status": "SuccessfullySignedUp"}
    
@router.post("/signIn")
def sign_in(data: SignInData, response: Response, db: Session = Depends(get_db)):
    print(f"Signing in user with email: {data.email}")
    user = db.query(Users).filter(Users.email == data.email).first()
    try:
        if user is None:
            print("Email does not exist.")
            return {"status": "emailAndPasswordDoesNotMatch"}
        if bcrypt.checkpw(data.passwordPlainText.encode('utf-8'), user.hashed_password.encode('utf-8')):
            print("Password is correct.")

            db_user_id = user.id
            db_user_name = user.user_name
            db_email = user.email
            db_user_roles = [r[0] for r in db.query(Roles.role_type).join(User_roles).filter(User_roles.user_id == db_user_id).all()]

            access_token = create_access_token(user_id=db_user_id, email=db_email, username=db_user_name, roles=db_user_roles)
            refresh_token = create_refresh_token(user_id=db_user_id)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,              # requires HTTPS in production
                samesite="lax",           # use "none" if cross-site + HTTPS
                path="/auth",             # limit cookie scope
                max_age=REFRESH_TTL,      # seconds (e.g., 14 days)
            )

            # 4) return access token in JSON
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TTL,  # seconds (e.g., 900)
                "user": {"id": db_user_id, "email": db_email, "username": db_user_name, "roles": db_user_roles},
            }

            # print(f"User ID: {db_user_id}, Username: {db_user_name}, Email: {db_email}, Roles: {db_user_roles}")

            # return {"status": "SuccessfullySignedIn", "username": user.user_name}
        else:
            print("Password is incorrect.")
            return {"status": "emailAndPasswordDoesNotMatch"}
    except Exception as e:
        print(f"Error during sign in: {e}")
        return {"status": "signInFailed"}
    

@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    rt = request.cookies.get("refresh_token")
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        data = verify_refresh(rt)        # validates signature/iss/aud/exp/typ
        uid = int(data["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.get(Users, uid)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    roles = [r.role_type for r in user.roles]
    new_access  = create_access_token(user_id=user.id, email=user.email, username=user.user_name, roles=roles)
    new_refresh = create_refresh_token(user_id=user.id)  # rotate refresh

    # set rotated refresh cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth",
        max_age=REFRESH_TTL,
    )
    return {"access_token": new_access, "token_type": "Bearer", "expires_in": ACCESS_TTL}

# --------- LOGOUT: clear cookie ---------
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/auth")
    return {"ok": True}
        