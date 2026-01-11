from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import Train, TrainCreate, TrainSearchRequest, TrainSearchResponse
from app.models import Train as TrainModel, Route as RouteModel, TrainSchedule as TrainScheduleModel
from app.services import TrainService
from app.api.auth import get_admin_user, get_current_user

router = APIRouter(prefix="/trains", tags=["Trains"])

@router.post("/", response_model=Train)
def create_train(
    train: TrainCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    try:
        return TrainService.create_train(db, train)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Train])
def get_trains(db: Session = Depends(get_db)):
    return TrainService.get_all_trains(db)

@router.get("/{train_id}", response_model=Train)
def get_train(
    train_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    train = TrainService.get_train(db, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

@router.put("/{train_id}", response_model=Train)
def update_train(
    train_id: int,
    train: TrainCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    updated_train = TrainService.update_train(db, train_id, train)
    if not updated_train:
        raise HTTPException(status_code=404, detail="Train not found")
    return updated_train

@router.patch("/{train_id}/toggle-status")
def toggle_train_status(
    train_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    result = TrainService.toggle_train_status(db, train_id)
    if not result:
        raise HTTPException(status_code=404, detail="Train not found")
    return result

@router.patch("/sync-routes")
def sync_routes_with_trains(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Sync all routes status with their associated trains"""
    result = TrainService.sync_routes_with_trains(db)
    return result

@router.delete("/{train_id}")
def delete_train(
    train_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    result = TrainService.delete_train(db, train_id)
    if not result:
        raise HTTPException(status_code=404, detail="Train not found")
    return result

@router.get("/admin/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    return TrainService.get_admin_dashboard(db)

@router.post("/search", response_model=List[TrainSearchResponse])
def search_trains(
    search_request: TrainSearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    schedules = TrainService.search_trains(db, search_request)
    
    results = []
    for schedule in schedules:
        results.append(TrainSearchResponse(
            schedule_id=schedule.id,
            train=schedule.route.train,
            route=schedule.route,
            schedule_date=schedule.schedule_date,
            available_seats=schedule.available_seats,
            departure_time=schedule.route.departure_time,
            arrival_time=schedule.route.arrival_time,
            base_fare=schedule.route.base_fare
        ))
    
    return results