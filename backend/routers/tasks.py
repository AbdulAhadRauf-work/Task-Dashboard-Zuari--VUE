
# backend/routers/tasks.py
# --- Final Version ---

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, schemas, models
from dependencies import get_db, get_current_active_user, require_roles

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/dashboard/{dashboard_id}", response_model=List[schemas.Task])
def read_tasks_for_dashboard(dashboard_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.get_tasks_for_dashboard(db=db, dashboard_id=dashboard_id, current_user=current_user)

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles([models.Role.CEO, models.Role.MANAGER]))):
    return crud.create_task(db=db, task=task)

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles([models.Role.CEO, models.Role.MANAGER]))):
    db_task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/{task_id}/assign/{user_id}", response_model=schemas.Task)
def assign_worker_to_task(task_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles([models.Role.CEO, models.Role.MANAGER]))):
    db_task = crud.assign_worker_to_task(db=db, task_id=task_id, user_id=user_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task or User not found")
    return db_task