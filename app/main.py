from fastapi import FastAPI 

from fastapi.middleware.cors import CORSMiddleware
from .routes import s3Test
from .routes import eventInfo



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


app.include_router(s3Test.router)
app.include_router(eventInfo.router)




