from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
try:
    try:
        if os.environ['FLASK_ENV'] == "development":
            import settings
            engine = create_engine(settings.DATABASE_URL, convert_unicode=True)
    except:
        engine = create_engine(os.environ['DATABASE_URL'], convert_unicode=True)
except:
    import settings
    engine = create_engine(settings.DATABASE_URL, convert_unicode=True)
    
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
