# reset_db.py
from sqlalchemy import text
from app.database import engine, Base
from app import models

print("⚠️  WARNING: NUKING DATABASE (FORCE RESET WITH CASCADE)...")

with engine.connect() as connection:
    # Start a transaction
    trans = connection.begin()
    
    try:
        print("Executing DROP CASCADE commands...")
        
        # 1. Kill the zombie table causing the error (note_history)
        connection.execute(text("DROP TABLE IF EXISTS note_history CASCADE;"))
        
        # 2. Kill the active tables
        connection.execute(text("DROP TABLE IF EXISTS note_versions CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS notes CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        
        # Confirm changes
        trans.commit()
        print("All tables dropped successfully.")
        
    except Exception as e:
        trans.rollback()
        print(f"❌ Error during drop: {e}")
        raise e

# 3. Re-create tables fresh from your models
print("Re-creating tables from models...")
Base.metadata.create_all(bind=engine)

print("✅ SUCCESS: Database is clean and ready!")