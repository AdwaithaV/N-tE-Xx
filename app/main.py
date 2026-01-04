# app/main.py
from fastapi import FastAPI
from .database import engine, Base
from . import models  # <--- CRITICAL: This forces the models to load

# Create tables automatically
# This checks your Neon DB. If tables are missing, it creates them.
# Base.metadata.create_all(bind=engine)

from .routers import auth, notes

app = FastAPI(title="Notes API with Version History")

app.include_router(auth.router, prefix="/auth")
app.include_router(notes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Notes API"}