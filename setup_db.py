# setup_db.py
from app.database import engine, Base
from app import models

print("Connecting to database...")
print(f"Using URL: {engine.url}")

print("Creating tables (users, notes, note_versions)...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ SUCCESS: Tables created successfully!")
except Exception as e:
    print(f"❌ ERROR: Could not create tables.")
    print(e)