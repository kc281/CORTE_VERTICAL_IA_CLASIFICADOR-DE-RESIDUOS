import os
from urllib.parse import quote_plus # <-- IMPORTANTE
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# 1. Obtenemos la URL cruda (con la contraseña sin codificar)
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise ValueError("❌ ERROR: La variable DATABASE_URL no está definida.")

# 2. Separamos la URL para codificar solo la contraseña de forma segura
#    (asumiendo el formato: scheme://user:password@host:port/db)
try:
    scheme, rest = raw_url.split("://", 1)
    userinfo, hostinfo = rest.rsplit("@", 1)
    user, password = userinfo.split(":", 1)
    
    # Codificamos la contraseña
    encoded_password = quote_plus(password)
    
    # Reconstruimos la URL con la contraseña segura
    safe_url = f"{scheme}://{user}:{encoded_password}@{hostinfo}"
    print("✅ URL de base de datos normalizada (contraseña codificada).")
except Exception as e:
    print(f"⚠️ No se pudo normalizar la URL, usando la original: {e}")
    safe_url = raw_url

# 3. Creamos el engine con la URL segura
engine = create_engine(safe_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()