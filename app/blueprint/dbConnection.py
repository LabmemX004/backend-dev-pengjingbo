from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

db_username = os.getenv("db_username")
db_password = os.getenv("db_password")
db_hostname = os.getenv("db_hostname")
db_port = os.getenv("db_port")
db_database = os.getenv("db_database")

db_url = f"mysql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_database}"

engine = create_engine(db_url)

Base = declarative_base()

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)