import os
import certifi
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.database import Base, engine 

# --- CRITICAL FIX: IMPORT MODELS ---
# This registers the tables (curriculum, job_role, etc.) with SQLAlchemy
import app.models 

load_dotenv("app/.env")

def reset_database():
    print("🔥 Starting Database Reset on TiDB...")
    
    with engine.connect() as connection:
        print("   Disabling Foreign Key Checks...")
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # List of tables to drop
        tables_to_drop = [
            "gap_report", 
            "skill_match_detail", 
            "match_result", 
            "course_skill", 
            "job_skill", 
            "embedding", 
            "curriculum", 
            "job_role", 
            "skill"
        ]
        
        for table in tables_to_drop:
            try:
                print(f"   Dropping table: {table}...", end=" ")
                connection.execute(text(f"DROP TABLE IF EXISTS {table};"))
                print("✅")
            except Exception as e:
                print(f"❌ (Error: {e})")

        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        connection.commit()
    
    print("🗑️  All tables dropped.")

    # Now this will actually work because app.models is imported!
    print("🏗️  Recreating tables from models.py...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    reset_database()