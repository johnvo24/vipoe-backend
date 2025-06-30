from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CollectionPoem
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/{poem_id}", status_code=status.HTTP_201_CREATED)
def save_poem_to_collection(
  poem_id: int,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  exists = db.query(CollectionPoem).filter_by(user_id=current_user.id, poem_id=poem_id).first()
  if exists:
    raise HTTPException(status_code=400, detail="Poem already saved")
  collection_poem = CollectionPoem(user_id=current_user.id, poem_id=poem_id)
  db.add(collection_poem)
  db.commit()
  return {"message": "Saved to collection"}

@router.delete("/{poem_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_poem_from_collection(
  poem_id: int,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  collection_poem = db.query(CollectionPoem).filter_by(user_id=current_user.id, poem_id=poem_id).first()
  if not collection_poem:
      raise HTTPException(status_code=404, detail="Poem not saved in collection")
  db.delete(collection_poem)
  db.commit()
  return