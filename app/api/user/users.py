from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserUpdate, UserRead
from app.utils.cloud_utils import upload_image_to_cloud
from app.core.security.jwt import create_jwt_token
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserRead)
def get_profile(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  user = db.query(User).filter(User.id == current_user.id).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.put("/profile", response_model=UserRead)
def update_profile(
  update_data: UserUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  user = db.query(User).filter(User.id == current_user.id).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  for field, value in update_data.dict(exclude_unset=True).items():
    setattr(user, field, value)
  user.updated_at = datetime.now(timezone.utc)

  db.commit()
  db.refresh(user)
  return user

@router.put("/profile/avatar", response_model=UserRead)
async def update_avatar(
  avatar: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  user = db.query(User).filter(User.id == current_user.id).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  try:
    avatar_url = await upload_image_to_cloud(avatar)
    user.avt_url = avatar_url
    user.updated_at = datetime.now(timezone.utc)
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading avatar: {str(e)}")
  
  db.commit()
  db.refresh(user)
  return user

# @router.get("/show-writers", response_model=list[ShowWriterResponse])
# async def get_all_writers(
#   db: Session = Depends(get_db)
# ):
#   writers = (
#     db.query(
#       User.id.label("user_id"),
#       User.full_name.label("full_name")
#     ).all()
#   )

#   result = [
#     {
#       "user_id": item.user_id,
#       "full_name": item.full_name,
#       "avatar": "https://upload.wikimedia.org/wikipedia/commons/2/21/Johnny_Depp_2020.jpg"
#     }
#     for item in writers
#   ]

#   return result