from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import dotenv
import os
from sqlalchemy.orm import DeclarativeBase

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,echo=True)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()