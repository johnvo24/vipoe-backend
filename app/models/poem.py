from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Poem(Base):
    __tablename__ = "poems"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    note = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    genre = relationship("Genre", back_populates="poems")
    user = relationship("User", back_populates="poems")
    comments = relationship("Comment", back_populates="poem")
    poem_likes = relationship("PoemLike", back_populates="poem")
    poem_tags = relationship("PoemTag", back_populates="poem")
    reports = relationship("Report", back_populates="poem")
    collection_poems = relationship("CollectionPoem", back_populates="poem")

class PoemTag(Base):
    __tablename__ = "poem_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    poem = relationship("Poem", back_populates="poem_tags")
    tag = relationship("Tag", back_populates="poem_tags")

class PoemLike(Base):
    __tablename__ = "poem_likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poem_id = Column(Integer, ForeignKey("poems.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="poem_likes")
    poem = relationship("Poem", back_populates="poem_likes")
