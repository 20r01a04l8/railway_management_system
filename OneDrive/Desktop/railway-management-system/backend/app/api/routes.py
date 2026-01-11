from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import Route, RouteCreate
from app.services import RouteService
from app.api.auth import get_admin_user, get_current_user

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.post("/", response_model=Route)
def create_route(
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    try:
        return RouteService.create_route(db, route)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Route])
def get_routes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return RouteService.get_all_routes(db)

@router.get("/{route_id}", response_model=Route)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    route = RouteService.get_route(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.put("/{route_id}", response_model=Route)
def update_route(
    route_id: int,
    route: RouteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    updated_route = RouteService.update_route(db, route_id, route)
    if not updated_route:
        raise HTTPException(status_code=404, detail="Route not found")
    return updated_route

@router.post("/bulk-create-schedules")
def bulk_create_schedules(
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create schedules for all active routes"""
    try:
        routes = RouteService.get_all_routes(db)
        created_count = 0
        
        for route in routes:
            RouteService.create_schedules_for_route(db, route.id, days_ahead)
            created_count += 1
        
        return {"message": f"Schedules created for {created_count} routes for next {days_ahead} days"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{route_id}/create-schedules")
def create_schedules_for_route(
    route_id: int,
    days_ahead: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create train schedules for a specific route"""
    try:
        RouteService.create_schedules_for_route(db, route_id, days_ahead)
        return {"message": f"Schedules created for route {route_id} for next {days_ahead} days"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{route_id}")
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    result = RouteService.delete_route(db, route_id)
    if not result:
        raise HTTPException(status_code=404, detail="Route not found")
    return result