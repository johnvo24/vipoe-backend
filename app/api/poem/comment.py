from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment
from app.schemas.poem import CommentCreate, CommentResponse
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/{poem_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
  poem_id: int,
  comment: CommentCreate,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  new_comment = Comment(
    user_id=current_user.id,
    poem_id=poem_id,
    content=comment.content
  )
  db.add(new_comment)
  db.commit()
  db.refresh(new_comment)
  return CommentResponse(
    id=new_comment.id,
    user_id=new_comment.user_id,
    poem_id=new_comment.poem_id,
    content=new_comment.content,
    created_at=new_comment.created_at,
    user_name=current_user.username,
    full_name=current_user.full_name,
    avt_url=current_user.avt_url
  )

@router.get("/{poem_id}/comments", response_model=list[CommentResponse])
def get_comments(
  poem_id: int,
  db: Session = Depends(get_db)
):
  comments = db.query(Comment).filter(Comment.poem_id == poem_id).order_by(Comment.created_at.asc()).all()
  return [
    CommentResponse(
      id=comment.id,
      user_id=comment.user_id,
      poem_id=comment.poem_id,
      content=comment.content,
      created_at=comment.created_at,
      user_name=comment.user.username,
      full_name=comment.user.full_name,
      avt_url=comment.user.avt_url
    ) for comment in comments
  ]

@router.put("/{poem_id}/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
  poem_id: int,
  comment_id: int,
  comment_update: CommentCreate,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  comment = db.query(Comment).filter(Comment.id == comment_id, Comment.poem_id == poem_id, Comment.user_id == current_user.id).first()
  if not comment:
    raise HTTPException(status_code=404, detail="Comment not found or not authorized")
  comment.content = comment_update.content
  db.commit()
  db.refresh(comment)
  return CommentResponse(
    id=comment.id,
    user_id=comment.user_id,
    poem_id=comment.poem_id,
    content=comment.content,
    created_at=comment.created_at,
    user_name=current_user.username,
    full_name=current_user.full_name,
    avt_url=current_user.avt_url
  )

@router.delete("/{poem_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
  poem_id: int,
  comment_id: int,
  db: Session = Depends(get_db),
  current_user = Depends(get_current_user)
):
  comment = db.query(Comment).filter(Comment.id == comment_id, Comment.poem_id == poem_id, Comment.user_id == current_user.id).first()
  if not comment:
    raise HTTPException(status_code=404, detail="Comment not found or not authorized")
  db.delete(comment)
  db.commit()
  return