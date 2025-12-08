import os
import certifi
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.database import Base, engine  # Import your existing engine/base

# Load env to be safe
load_dotenv("app/.env")

def reset_database():
    print("🔥 Starting Database Reset on TiDB...")
    
    # 1. Connect and Disable Foreign Key Checks (The "Force" Button)
    with engine.connect() as connection:
        print("   Disabling Foreign Key Checks...")
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # 2. Drop Tables Explicitly (Order doesn't matter much with checks off, but good practice)
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

        # 3. Re-enable Checks
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        connection.commit()
    
    print("🗑️  All tables dropped successfully.")

    # 4. Recreate Tables using SQLAlchemy models
    print("🏗️  Recreating tables from models.py...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database is fresh and ready!")

if __name__ == "__main__":
    reset_database()