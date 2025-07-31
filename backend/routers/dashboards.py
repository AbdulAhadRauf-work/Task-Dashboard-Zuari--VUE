
# backend/routers/dashboards.py
# --- Final Version ---

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, schemas, models
from dependencies import get_db, get_current_active_user, require_roles, require_role

router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=List[schemas.Dashboard])
def read_dashboards(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.get_dashboards(db=db, current_user=current_user)

@router.post("/", response_model=schemas.Dashboard, status_code=status.HTTP_201_CREATED)
def create_dashboard(dashboard: schemas.DashboardCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles([models.Role.CEO, models.Role.MANAGER]))):
    return crud.create_dashboard(db=db, dashboard=dashboard, owner_id=current_user.id)

@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.Role.CEO))):
    db_dashboard = crud.delete_dashboard(db=db, dashboard_id=dashboard_id)
    if db_dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return