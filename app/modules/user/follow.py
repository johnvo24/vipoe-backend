from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models import User, Follow

def follow_user(db: Session, follower_id: int, followed_id: int):
    if follower_id == followed_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
    ).first()
    if existing_follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following this user")
    
    # Check if followed user exists
    followed_user = db.query(User).filter(User.id == followed_id).first()
    if not followed_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to follow not found")
    
    follow = Follow(follower_id=follower_id, followed_id=followed_id)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow

def unfollow_user(db: Session, follower_id: int, followed_id: int):
    follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
    ).first()
    if not follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following this user")
    
    db.delete(follow)
    db.commit()
    return {"message": "Unfollowed successfully"}

def get_followers(db: Session, user_id: int):
    followers = db.query(Follow).filter(Follow.followed_id == user_id).all()
    return followers

def get_following(db: Session, user_id: int):
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    return following

def is_following(db: Session, follower_id: int, followed_id: int):
    follow = db.query(Follow).filter(
        and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
    ).first()
    return follow is not None

def get_followers_count(db: Session, user_id: int):
    return db.query(Follow).filter(Follow.followed_id == user_id).count()

def get_following_count(db: Session, user_id: int):
    return db.query(Follow).filter(Follow.follower_id == user_id).count()