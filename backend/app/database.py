from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.models import Base

load_dotenv()
db_url = os.getenv("DATABASE_URL")

# engine = create_engine(f"postgresql://{user}:{password}@localhost/companion", echo=True)
engine = create_engine(db_url, echo=True)
Base.metadata.create_all(engine)  # create tables if they don't exist
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
