from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Your Neon Connection String
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_K8HE0DAgwqYI@ep-mute-bird-ahq3zhm7-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# UPDATE: Added pool_pre_ping=True to fix SSL drops
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()