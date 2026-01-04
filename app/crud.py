from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Auth Utilities ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# --- Note Logic ---
def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    db_note = models.Note(**note.dict(), owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes(db: Session, user_id: int):
    return db.query(models.Note).filter(models.Note.owner_id == user_id).all()

def get_note_by_id(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

# --- THE VERSIONING MAGIC ---
def update_note(db: Session, note_id: int, note_update: schemas.NoteUpdate, user_id: int):
    # 1. Fetch the note to be updated
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        return None

    # 2. Create a snapshot of the current state (Read-Copy-Update)
    # This snapshot is saved to the history table.
    
    # Calculate the next version number
    last_version = db.query(func.max(models.NoteVersion.version)).filter(models.NoteVersion.note_id == note_id).scalar() or 0
    new_version = last_version + 1

    history_entry = models.NoteVersion(
        note_id=db_note.id,
        version=new_version,
        editor_id=user_id,
        title=db_note.title, # Snapshot title
        content=db_note.content # Snapshot content
    )
    db.add(history_entry) # Stage for saving

    # 3. Apply updates to the note content
    if note_update.title:
        db_note.title = note_update.title
    if note_update.content:
        db_note.content = note_update.content
    
    # 4. Save everything (the new history entry AND the updated note) in one go
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note_history(db: Session, note_id: int):
    return db.query(models.NoteVersion).filter(models.NoteVersion.note_id == note_id).order_by(models.NoteVersion.version.desc()).all()

def get_note_version(db: Session, note_id: int, version: int):
    return db.query(models.NoteVersion).filter(models.NoteVersion.note_id == note_id, models.NoteVersion.version == version).first()

def restore_note_version(db: Session, note_id: int, version: int, user_id: int):
    # Retrieve the specific history version to restore
    version_snapshot = get_note_version(db, note_id, version)
    if not version_snapshot:
        return None
    
    db_note = get_note_by_id(db, note_id)
    if not db_note:
        return None
        
    # Treat restoration as an update: save the current state as a new version
    # before overwriting with historical data to prevent data loss.
    
    last_version = db.query(func.max(models.NoteVersion.version)).filter(models.NoteVersion.note_id == note_id).scalar() or 0
    new_version = last_version + 1
    
    history_entry = models.NoteVersion(
        note_id=db_note.id,
        version=new_version,
        editor_id=user_id,
        title=db_note.title,
        content=db_note.content
    )
    db.add(history_entry)
    
    # Overwrite current note with snapshot data
    db_note.title = version_snapshot.title
    db_note.content = version_snapshot.content
    
    db.commit()
    db.refresh(db_note)
    return db_note