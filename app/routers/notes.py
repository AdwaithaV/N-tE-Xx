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
    """
    Update a note's title or content.
    Automatically creates a new version in the history entry for rollback purposes.
    """
    # Verify ownership before updating
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this note")
    
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

@router.get("/{note_id}/versions/{version_id}", response_model=schemas.NoteVersionResponse)
def get_version(note_id: int, version_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Verify ownership
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    version = crud.get_note_version(db, note_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/{note_id}/restore/{version_id}", response_model=schemas.NoteResponse)
def restore_version(note_id: int, version_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Roll back a note to a previous version. 
    Functionally works as an update, treating the restored content as a new edit 
    to preserve the history chain.
    """
    # Verify ownership
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to restore this note")
        
    restored_note = crud.restore_note_version(db, note_id, version_id, current_user.id)
    if not restored_note:
        raise HTTPException(status_code=404, detail="Version not found or restore failed")
    
    return restored_note