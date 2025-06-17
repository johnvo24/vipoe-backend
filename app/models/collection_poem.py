from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database import Base

class CollectionPoem(Base):
    __tablename__ = "collection_poems"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="collection_poems")
    poem = relationship("Poem", back_populates="collection_poems")
