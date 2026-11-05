import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL  # Importante para construir la URL
from dotenv import load_dotenv

load_dotenv()

# 1. Obtenemos la URL cruda desde la variable de entorno
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise ValueError("❌ ERROR: La variable DATABASE_URL no está definida en el entorno.")

# 2. Usamos URL.create() para parsear la URL de forma segura.
#    SQLAlchemy se encarga de todo el manejo de caracteres especiales.
#    El prefijo 'postgresql+psycopg2' le dice que use el driver que instalamos.
try:
    # URL.create() puede tomar la URL completa como string y parsearla.
    # Es mucho más robusto que la manipulación manual de strings.
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        # Pasamos la URL completa para que extraiga usuario, contraseña, host, etc.
        # SQLAlchemy se encargará de la codificación necesaria.
        url=raw_url
    )
    print("✅ URL de base de datos parseada correctamente con URL.create().")
except Exception as e:
    print(f"❌ Error al parsear la URL: {e}")
    # Si falla el parseo, es mejor detener la aplicación con un error claro.
    raise

# 3. Creamos el engine con la URL segura
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()