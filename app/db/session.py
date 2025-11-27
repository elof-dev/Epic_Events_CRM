from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

def get_database_url(db_name=None):
    db = db_name or DB_NAME
    user = DB_USER
    password = DB_PASS or ""
    host = DB_HOST
    port = DB_PORT
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"


def create_engine_and_session(db_name=None, **kwargs):
    url = get_database_url(db_name)
    engine = create_engine(url, future=True, echo=False, **kwargs)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine, SessionLocal
