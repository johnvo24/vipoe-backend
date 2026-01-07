from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from app.schemas.user import UserRead, UserAdminUpdate, UserCreate
from app.utils.cloud_utils import upload_image_to_cloud
from app.core.security.bcrypt_hashing import hash_password
from app.auth.dependencies import get_current_admin

admin_router = APIRouter(dependencies=[Depends(get_current_admin)])

@admin_router.get("/", response_model=list[UserRead])
def get_all_users(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  users = db.query(User).offset(skip).limit(limit).all()
  return users

@admin_router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
  user_id: int,
  db: Session = Depends(get_db)
):
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@admin_router.put("/{user_id}", response_model=UserRead)
def update_user_by_admin(
  user_id: int,
  update_data: UserAdminUpdate,
  db: Session = Depends(get_db)
):
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  for field, value in update_data.dict(exclude_unset=True).items():
    setattr(user, field, value)
  user.updated_at = datetime.now(timezone.utc)

  db.commit()
  db.refresh(user)
  return user

@admin_router.delete("/{user_id}")
def delete_user_by_admin(
  user_id: int,
  db: Session = Depends(get_db)
):
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  db.delete(user)
  db.commit()
  return {"message": "User deleted successfully"}

@admin_router.post("/", response_model=UserRead)
def create_user_by_admin(
  user_data: UserCreate,
  db: Session = Depends(get_db)
):
  # Check if username or email already exists
  existing_user = db.query(User).filter(
    (User.username == user_data.username) | (User.email == user_data.email)
  ).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Username or email already exists")
  
  hashed_password = hash_password(user_data.password)
  
  new_user = User(
    full_name=user_data.full_name,
    username=user_data.username,
    email=user_data.email,
    password=hashed_password,
    role="user"  # Default role
  )
  
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user