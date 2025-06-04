from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="collections")
    collection_poems = relationship("CollectionPoem", back_populates="collection")

class CollectionPoem(Base):
    __tablename__ = "collection_poems"
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=False)

    collection = relationship("Collection", back_populates="collection_poems")
    poem = relationship("Poem", back_populates="collection_poems")
