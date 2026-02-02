from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
port = os.getenv("DB_PORT")

SQL_DB_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(SQL_DB_URL)
Sessions = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Sessions()
    try:
        yield db
    finally:
        db.close()
