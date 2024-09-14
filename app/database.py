from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager

# Use this for PostgreSQL:
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

GLOBAL = {}
Base = declarative_base()

def _singleton_sessionLocal():
    SessionLocal = GLOBAL.get('SessionLocal')
    if SessionLocal:
        return SessionLocal
    database_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    GLOBAL['engine'] = engine
    GLOBAL['SessionLocal'] = SessionLocal
    return SessionLocal

def create_tables():
    import models
    _singleton_sessionLocal()
    engine = GLOBAL['engine']
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@contextmanager
def dbsession():
    SessionLocal = _singleton_sessionLocal()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()