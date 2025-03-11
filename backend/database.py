import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:root@127.0.0.1/jobboard")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def connect_redis():
    try:
        client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        client.ping()
        print("Connected to Redis!")
        return client
    except redis.ConnectionError as e:
        print(f"Redis connection failed: {e}")
        return None  

redis_client = connect_redis()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
