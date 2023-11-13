from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.models import Base

load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

engine = create_engine(f"postgresql://{user}:{password}@localhost/companion", echo=True)
Base.metadata.create_all(engine)  # create tables if don't exist
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
