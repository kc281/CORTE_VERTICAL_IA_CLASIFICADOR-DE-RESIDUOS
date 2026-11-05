from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app import config
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de la BD en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()