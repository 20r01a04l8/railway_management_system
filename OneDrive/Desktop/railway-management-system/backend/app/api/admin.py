from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.models import SystemAlert, Train, Booking, TrainSchedule, AlertType, User
from app.api.auth import get_admin_user
from datetime import datetime, timedelta
from typing import List
from app.services import RefundService
from app.schemas import RefundRequest, RefundRequestUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/system-alerts")
def get_system_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    # Get existing active alerts
    alerts = db.query(SystemAlert).filter(SystemAlert.is_active == True).order_by(SystemAlert.created_at.desc()).all()
    
    # Generate new alerts based on system conditions
    new_alerts = generate_system_alerts(db)
    
    # Combine and return
    all_alerts = []
    
    # Add existing alerts
    for alert in alerts:
        all_alerts.append({
            "id": str(alert.id),
            "type": alert.alert_type.value,
            "icon": alert.icon,
            "title": alert.title,
            "message": alert.message,
            "time": format_time_ago(alert.created_at),
            "dismissible": alert.dismissible
        })
    
    # Add new generated alerts
    all_alerts.extend(new_alerts)
    
    return all_alerts

@router.post("/system-alerts/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    alert = db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    db.commit()
    return {"message": "Alert dismissed"}

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

@router.patch("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own account")
    
    user.is_active = not user.is_active
    db.commit()
    
    status = "activated" if user.is_active else "blocked"
    return {"message": f"User {status} successfully", "is_active": user.is_active}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    from app.models import Booking, Passenger
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    try:
        # Delete passengers from user's bookings
        bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
        for booking in bookings:
            db.query(Passenger).filter(Passenger.booking_id == booking.id).delete()
        
        # Delete user's bookings
        db.query(Booking).filter(Booking.user_id == user_id).delete()
        
        # Delete the user
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

def generate_system_alerts(db: Session):
    alerts = []
    now = datetime.utcnow()
    
    # Check for inactive trains
    inactive_trains = db.query(Train).filter(Train.is_active == False).count()
    if inactive_trains > 0:
        # Check if this alert already exists in last hour
        existing = db.query(SystemAlert).filter(
            and_(
                SystemAlert.title == "Inactive Trains",
                SystemAlert.created_at > now - timedelta(hours=1),
                SystemAlert.is_active == True
            )
        ).first()
        
        if not existing:
            alert = SystemAlert(
                alert_type=AlertType.warning,
                title="Inactive Trains",
                message=f"{inactive_trains} train(s) are currently inactive",
                icon="train",
                dismissible=True
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            alerts.append({
                "id": str(alert.id),
                "type": "warning",
                "icon": "train",
                "title": "Inactive Trains",
                "message": f"{inactive_trains} train(s) are currently inactive",
                "time": "Just now",
                "dismissible": True
            })
    
    # Check for high booking volume (more than 5 bookings in last hour)
    recent_bookings = db.query(Booking).filter(
        Booking.booking_date > now - timedelta(hours=1)
    ).count()
    
    if recent_bookings > 5:
        existing = db.query(SystemAlert).filter(
            and_(
                SystemAlert.title == "High Booking Volume",
                SystemAlert.created_at > now - timedelta(hours=1),
                SystemAlert.is_active == True
            )
        ).first()
        
        if not existing:
            alert = SystemAlert(
                alert_type=AlertType.info,
                title="High Booking Volume",
                message=f"{recent_bookings} bookings in the last hour",
                icon="chart-line",
                dismissible=True
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            alerts.append({
                "id": str(alert.id),
                "type": "info",
                "icon": "chart-line",
                "title": "High Booking Volume",
                "message": f"{recent_bookings} bookings in the last hour",
                "time": "Just now",
                "dismissible": True
            })
    
    # Check for low seat availability
    low_seat_schedules = db.query(TrainSchedule).filter(
        and_(
            TrainSchedule.available_seats < 10,
            TrainSchedule.schedule_date >= datetime.now().date()
        )
    ).count()
    
    if low_seat_schedules > 0:
        existing = db.query(SystemAlert).filter(
            and_(
                SystemAlert.title == "Low Seat Availability",
                SystemAlert.created_at > now - timedelta(hours=2),
                SystemAlert.is_active == True
            )
        ).first()
        
        if not existing:
            alert = SystemAlert(
                alert_type=AlertType.warning,
                title="Low Seat Availability",
                message=f"{low_seat_schedules} schedule(s) have less than 10 seats available",
                icon="exclamation-triangle",
                dismissible=True
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            alerts.append({
                "id": str(alert.id),
                "type": "warning",
                "icon": "exclamation-triangle",
                "title": "Low Seat Availability",
                "message": f"{low_seat_schedules} schedule(s) have less than 10 seats available",
                "time": "Just now",
                "dismissible": True
            })
    
    return alerts

@router.get("/refund-requests", response_model=List[RefundRequest])
def get_pending_refund_requests(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    return RefundService.get_pending_refund_requests(db)

@router.put("/refund-requests/{request_id}/approve")
def approve_refund_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    try:
        refund_request = RefundService.approve_refund_request(db, request_id, current_user.id)
        return {"message": "Refund request approved and processed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/refund-requests/{request_id}/reject")
def reject_refund_request(
    request_id: int,
    update: RefundRequestUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    try:
        refund_request = RefundService.reject_refund_request(db, request_id, current_user.id, update.rejection_reason)
        return {"message": "Refund request rejected"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def format_time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"