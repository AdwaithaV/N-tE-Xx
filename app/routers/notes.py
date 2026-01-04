# app/routers/notes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=schemas.NoteResponse)
def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_note(db=db, note=note, user_id=current_user.id)

@router.get("/", response_model=List[schemas.NoteResponse])
def read_notes(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_notes(db, user_id=current_user.id)

@router.put("/{note_id}", response_model=schemas.NoteResponse)
def update_note(note_id: int, note_update: schemas.NoteUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Verify ownership
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.update_note(db=db, note_id=note_id, note_update=note_update, user_id=current_user.id)

@router.get("/{note_id}/history", response_model=List[schemas.NoteVersionResponse])
def get_history(note_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Verify ownership
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return crud.get_note_history(db, note_id)