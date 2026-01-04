from sqlalchemy.orm import Session
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
    # 1. Fetch current note
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        return None

    # 2. CREATE SNAPSHOT (Save current state to history)
    history_entry = models.NoteVersion(
        note_id=db_note.id,
        editor_id=user_id,
        title=db_note.title,
        content=db_note.content
    )
    db.add(history_entry) # Stage the history entry

    # 3. Update the actual note with new data
    if note_update.title:
        db_note.title = note_update.title
    if note_update.content:
        db_note.content = note_update.content
    
    # 4. Commit both changes in one transaction
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note_history(db: Session, note_id: int):
    return db.query(models.NoteVersion).filter(models.NoteVersion.note_id == note_id).all()