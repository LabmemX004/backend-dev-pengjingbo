from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

from app.routes import bookingTickets
from .routes import eventInfo
from .routes import signInAndUp
from .routes import userAccountPageAPI
from . import blueprint
#from .blueprint.dbConnection import engine, SessionLocal
from .blueprint.dbBlueprint import engine, SessionLocal 
import os


blueprint.dbBlueprint.Base.metadata.create_all(bind=engine)


app = FastAPI()

# Frontend dev origins you want to allow
origins = [
    "https://www.eventmaster.andrewzhangdev.com",
    "https://eventmaster.andrewzhangdev.com",
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(eventInfo.router)
app.include_router(signInAndUp.router)
app.include_router(bookingTickets.router)
app.include_router(userAccountPageAPI.router)

@app.get("/")
def read_root():
    return {"welcome to Student Event backend"}

import redis

# r = redis.Redis(host="localhost", port=6379, decode_responses=True)
# print(r.ping())

try:
    r = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDISPORT")),db=0, decode_responses=True)
    r.ping()
except Exception as e:
    try:
        r = redis.Redis(host=os.getenv("REDISURL"), port=int(os.getenv("REDISPORT")),db=0, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"both redis connection failed: {e}")




