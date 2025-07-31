# backend/routers/comments.py
# --- Corrected Version ---

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

import crud, schemas, models
from dependencies import get_db, get_current_active_user, require_roles
from connection_manager import manager

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
    dependencies=[Depends(get_current_active_user)]
)

UPLOAD_DIRECTORY = "./uploads"

@router.get("/task/{task_id}", response_model=List[schemas.Comment])
def read_comments_for_task(task_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.task_id == task_id, models.Comment.parent_id == None).order_by(models.Comment.created_at.asc()).all()
    return comments

@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
async def create_comment_with_file(content: str = Form(...), task_id: int = Form(...), parent_id: Optional[int] = Form(None), file: Optional[UploadFile] = File(None), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    comment_schema = schemas.CommentCreate(content=content, task_id=task_id, parent_id=parent_id)
    db_comment = crud.create_comment(db=db, comment=comment_schema, author_id=current_user.id)

    if file:
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path_on_disk = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        try:
            crud.save_upload_file(upload_file=file, destination=file_path_on_disk)
            # FIX: Store only the unique filename in the database, not the full disk path.
            # The frontend will construct the full URL to access the file.
            crud.create_file_record(db=db, file_name=file.filename, file_path=unique_filename, comment_id=db_comment.id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    db.refresh(db_comment)

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        user_ids_to_notify = [worker.id for worker in task.workers]
        if task.dashboard and task.dashboard.owner_id not in user_ids_to_notify:
            user_ids_to_notify.append(task.dashboard.owner_id)
        user_ids_to_notify = [uid for uid in user_ids_to_notify if uid != current_user.id]

        message = {"type": "new_comment", "payload": {"taskId": task_id, "commentId": db_comment.id, "authorName": current_user.full_name, "taskTitle": task.title}}
        await manager.broadcast_to_users(message, user_ids_to_notify)

    return db_comment

@router.put("/{comment_id}/status", response_model=schemas.Comment)
async def update_comment_status(comment_id: int, status_update: schemas.CommentStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles([models.Role.CEO, models.Role.MANAGER]))):
    db_comment = crud.update_comment_status(db=db, comment_id=comment_id, status=status_update)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if db_comment.author_id != current_user.id:
        message = {"type": "comment_status_update", "payload": {"taskId": db_comment.task_id, "commentId": comment_id, "status": db_comment.status.value, "reviewerName": current_user.full_name, "taskTitle": db_comment.task.title}}
        await manager.send_personal_message(message, db_comment.author_id)

    return db_comment
