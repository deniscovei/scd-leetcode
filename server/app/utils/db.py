from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

def init_db(app=None):
    # Import all models so they are registered with Base
    from app.models import user, problem, submission
    Base.metadata.create_all(bind=engine)

def get_session():
    return Session()
