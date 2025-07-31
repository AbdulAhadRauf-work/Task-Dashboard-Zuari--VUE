# backend/crud.py
# --- Corrected Version ---

from sqlalchemy.orm import Session, joinedload
import models, schemas, security
from typing import List
import shutil
from fastapi import UploadFile

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Dashboard CRUD ---
def get_dashboards(db: Session, current_user: models.User):
    # FIX: Eagerly load the tasks associated with each dashboard using joinedload.
    # This ensures that when the frontend fetches dashboards, the 'tasks' list is populated,
    # allowing the UI to correctly display the task count.
    if current_user.role == models.Role.CEO:
        return db.query(models.Dashboard).options(joinedload(models.Dashboard.owner), joinedload(models.Dashboard.tasks)).all()
    if current_user.role == models.Role.MANAGER:
        return db.query(models.Dashboard).filter(models.Dashboard.owner_id == current_user.id).options(joinedload(models.Dashboard.owner), joinedload(models.Dashboard.tasks)).all()
    if current_user.role == models.Role.WORKER:
        assigned_task_ids = db.query(models.TaskWorkers.task_id).filter(models.TaskWorkers.user_id == current_user.id).subquery()
        dashboard_ids = db.query(models.Task.dashboard_id).filter(models.Task.id.in_(assigned_task_ids)).distinct()
        return db.query(models.Dashboard).filter(models.Dashboard.id.in_(dashboard_ids)).options(joinedload(models.Dashboard.owner), joinedload(models.Dashboard.tasks)).all()
    return []

def create_dashboard(db: Session, dashboard: schemas.DashboardCreate, owner_id: int):
    db_dashboard = models.Dashboard(**dashboard.dict(), owner_id=owner_id)
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard

def delete_dashboard(db: Session, dashboard_id: int):
    db_dashboard = db.query(models.Dashboard).filter(models.Dashboard.id == dashboard_id).first()
    if db_dashboard:
        db.delete(db_dashboard)
        db.commit()
    return db_dashboard

# --- Task CRUD ---
def get_tasks_for_dashboard(db: Session, dashboard_id: int, current_user: models.User):
    query = db.query(models.Task).filter(models.Task.dashboard_id == dashboard_id).options(joinedload(models.Task.workers))
    if current_user.role == models.Role.WORKER:
        query = query.join(models.TaskWorkers).filter(models.TaskWorkers.user_id == current_user.id)
    return query.all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(title=task.title, description=task.description, deadline=task.deadline, dashboard_id=task.dashboard_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def assign_worker_to_task(db: Session, task_id: int, user_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_task and db_user and db_user not in db_task.workers:
        db_task.workers.append(db_user)
        db.commit()
        db.refresh(db_task)
    return db_task

# --- Comment and File CRUD ---
def get_comments_for_task(db: Session, task_id: int):
    return db.query(models.Comment).filter(models.Comment.task_id == task_id).options(joinedload(models.Comment.author), joinedload(models.Comment.files), joinedload(models.Comment.replies)).order_by(models.Comment.created_at.asc()).all()

def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    db_comment = models.Comment(**comment.dict(), author_id=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def create_file_record(db: Session, file_name: str, file_path: str, comment_id: int):
    db_file = models.File(file_name=file_name, file_path=file_path, comment_id=comment_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def save_upload_file(upload_file: UploadFile, destination: str):
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

def update_comment_status(db: Session, comment_id: int, status: schemas.CommentStatusUpdate):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        db_comment.status = status.status
        db.commit()
        db.refresh(db_comment)
    return db_comment
