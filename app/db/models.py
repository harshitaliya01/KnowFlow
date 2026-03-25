from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from app.db.session import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255),nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index= True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False, index=True)
    filepath = Column(String(255), nullable=False)
    source = Column(String(80), nullable=False)
    status = Column(String(50), default="Pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)  
    chunk_id = Column(String(100), unique=True, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False) 
    page = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())