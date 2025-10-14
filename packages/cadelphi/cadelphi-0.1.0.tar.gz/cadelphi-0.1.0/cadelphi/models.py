from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


Base = declarative_base()


class SelectionStrategy(str, Enum):
    RANDOM = "random"
    POSITIVE = "positive"
    NEGATIVE = "negative"


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    arguments: Mapped[List["Argument"]] = relationship(back_populates="author")
    votes: Mapped[List["Vote"]] = relationship(back_populates="participant")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    arguments: Mapped[List["Argument"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class Argument(Base):
    __tablename__ = "arguments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("participants.id", ondelete="SET NULL"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="arguments")
    author: Mapped[Optional[Participant]] = relationship(back_populates="arguments")
    votes: Mapped[List["Vote"]] = relationship(back_populates="argument", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("argument_id", "participant_id", name="uq_vote_argument_participant"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    argument_id: Mapped[int] = mapped_column(ForeignKey("arguments.id", ondelete="CASCADE"), nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    argument: Mapped[Argument] = relationship(back_populates="votes")
    participant: Mapped[Participant] = relationship(back_populates="votes")


class SelectionSession(Base):
    __tablename__ = "selection_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    assigned_argument_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=list)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    participant: Mapped[Participant] = relationship()
    topic: Mapped[Topic] = relationship()


class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    selection_strategy: Mapped[SelectionStrategy] = mapped_column(
        SqlEnum(SelectionStrategy), default=SelectionStrategy.RANDOM, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
