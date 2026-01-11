from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import Station, StationCreate
from app.services import StationService
from app.api.auth import get_admin_user, get_current_user

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.post("/", response_model=Station)
def create_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    return StationService.create_station(db, station)

@router.get("/", response_model=List[Station])
def get_stations(db: Session = Depends(get_db)):
    return StationService.get_all_stations(db)

@router.get("/{station_id}", response_model=Station)
def get_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    station = StationService.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    return station