from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Diary(Base):
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Changed from Integer to String
    name = Column(String(100), index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    entries = relationship("DiaryEntry", back_populates="diary")

class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    diary_id = Column(Integer, ForeignKey("diaries.id"), index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    diary = relationship("Diary", back_populates="entries")

class ZapMessage(Base):
    __tablename__ = "zap_messages"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String, index=True)
    group_name = Column(String)
    message_id = Column(String, index=True)
    message_type = Column(String)
    message_body = Column(Text)
    from_number = Column(String)
    from_name = Column(String)
    timestamp = Column(DateTime(timezone=True))
    deleted_on = Column(DateTime(timezone=True))
    is_edited = Column(Boolean, default=False)
    edited_id = Column(Integer, ForeignKey("zap_messages.id"))
