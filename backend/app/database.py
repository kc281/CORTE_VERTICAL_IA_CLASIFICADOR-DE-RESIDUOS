import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import make_url  
from dotenv import load_dotenv

load_dotenv()

raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise ValueError(" ERROR: La variable DATABASE_URL no está definida en el entorno.")

try:
 
    database_url = make_url(raw_url)
    print(" URL de base de datos parseada correctamente con make_url().")
except Exception as e:
    print(f" Error al parsear la URL: {e}")
    raise


engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()