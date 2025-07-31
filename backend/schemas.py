# backend/schemas.py
# --- Final Version ---

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from models import Role, CommentStatus
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Role = Role.WORKER

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: Role
    is_active: bool

    class Config:
        orm_mode = True

# --- File Schemas ---
class File(BaseModel):
    id: int
    file_name: str
    file_path: str

    class Config:
        orm_mode = True

# --- Comment Schemas ---
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: int
    parent_id: Optional[int] = None

class CommentStatusUpdate(BaseModel):
    status: CommentStatus

class Comment(CommentBase):
    id: int
    created_at: datetime
    author: User
    status: CommentStatus
    parent_id: Optional[int] = None
    replies: List['Comment'] = []
    files: List[File] = []

    class Config:
        orm_mode = True

Comment.update_forward_refs()

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    dashboard_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: int
    status: str
    workers: List[User] = []
    comments: List[Comment] = []

    class Config:
        orm_mode = True

# --- Dashboard Schemas ---
class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None

class DashboardCreate(DashboardBase):
    pass

class Dashboard(DashboardBase):
    id: int
    owner: User
    tasks: List[Task] = []

    class Config:
        orm_mode = True