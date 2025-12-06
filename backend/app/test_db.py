from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connected! Test query result:", result.scalar())
except Exception as e:
    print("❌ Connection failed:", e)