import os
import certifi  # <--- Make sure this is imported
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "4000") # TiDB defaults to 4000

# Convert DB_PORT to int
try:
    DB_PORT = int(DB_PORT)
except (ValueError, TypeError):
    DB_PORT = 4000

# Validate config
if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME]):
    print(f"WARNING: Missing database configuration. Using placeholder values.")

# --- THE FIX: Add SSL arguments for TiDB ---
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL, 
    echo=False,
    poolclass=NullPool,
    connect_args={
        "ssl_ca": certifi.where(),  # <--- Critical for TiDB
        "ssl_disabled": False
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()