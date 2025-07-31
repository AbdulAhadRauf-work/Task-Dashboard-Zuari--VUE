# backend/models.py
# --- Final Version (FIXED) ---

from sqlalchemy import (
    Boolean, Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from database import Base

class Role(str, Enum):
    CEO = "ceo"
    MANAGER = "manager"
    WORKER = "worker"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    role = Column(SQLAlchemyEnum(Role), default=Role.WORKER)
    is_active = Column(Boolean, default=True)

    dashboards = relationship("Dashboard", back_populates="owner")
    tasks_assigned = relationship("Task", secondary="task_workers")
    comments = relationship("Comment", back_populates="author")

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="dashboards")
    tasks = relationship("Task", back_populates="dashboard", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    deadline = Column(DateTime)
    status = Column(String, default="Pending")
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    
    dashboard = relationship("Dashboard", back_populates="tasks")
    workers = relationship("User", secondary="task_workers")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")

class TaskWorkers(Base):
    __tablename__ = "task_workers"
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task_id = Column(Integer, ForeignKey("tasks.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    status = Column(SQLAlchemyEnum(CommentStatus), default=CommentStatus.PENDING)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")
    
    # FIX: Added single_parent=True to the replies relationship to resolve the InvalidRequestError.
    # This tells SQLAlchemy that a child comment (a reply) will only have one parent,
    # making the 'delete-orphan' cascade safe to use.
    replies = relationship(
        "Comment",
        back_populates="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True
    )
    parent = relationship("Comment", back_populates="replies", remote_side=[parent_id])
    files = relationship("File", back_populates="comment", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id"))

    comment = relationship("Comment", back_populates="files")
