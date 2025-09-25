from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..blueprint.dbBlueprint import SessionLocal, Booking_ticket_action_info, Events, Users, User_roles, Roles
from ..auth.jwt_bearer import jwtBearer, get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/getUserInfo/{user_id}", dependencies=[Depends(jwtBearer())])
def get_user_info(user_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    if(int(current_user["user_id"]) != user_id):
        raise HTTPException(status_code=403, detail="User ID does not match the token")
    user = db.query(Users).filter(Users.id == user_id).first()
    user_roles = db.scalars(select(Roles.role_type).join(User_roles, User_roles.role_id == Roles.id).where(User_roles.user_id == user_id)).all()
    print(user_roles)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "roles": user_roles,
        "created_at": user.created_at,
    }

@router.get("/getUserBookedEventsInfo/{user_id}", dependencies=[Depends(jwtBearer())])
def get_user_booked_events_info(user_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    if(int(current_user["user_id"]) != user_id):
        raise HTTPException(status_code=403, detail="User ID does not match the token")
    bookings = db.query(Booking_ticket_action_info).filter(Booking_ticket_action_info.user_id == user_id).all()
    if not bookings:
        return {"message": "No bookings found for this user."}
    
    rows = (
        db.query(Booking_ticket_action_info, Events)
            .join(Events, Events.id == Booking_ticket_action_info.event_id)
            .filter(Booking_ticket_action_info.user_id == user_id)
            .order_by(Events.event_start_date_and_time.desc())  # full timestamp DESC (latest/farthest future first)
            .all()
    )

    booked_events_info = [
        {
            "booking_id": booking.id,
            "event_id": event.id,
            "event_title": event.event_title,
            "event_type": event.event_type,
            "event_provider_id": event.event_provider_id,
            "event_start_date_and_time": event.event_start_date_and_time,
            "event_lasting_time": event.event_duration_in_minutes,
            "event_location": event.event_location,
            "event_image": event.event_imageUrl,
            "event_description": event.event_description,
            "number_of_tickets_booked": booking.number_of_tickets,
            "booking_status": booking.status,
            "ticket_code": booking.ticket_code,
        }
        for booking, event in rows
    ]
    return booked_events_info

@router.get("/getEventsThatProvidedByTheUser/{user_id}", dependencies=[Depends(jwtBearer())])
def get_events_provided_by_user(user_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    if(int(current_user["user_id"]) != user_id):
        raise HTTPException(status_code=403, detail="User ID does not match the token")
    events = db.query(Events).filter(Events.event_provider_id == user_id).order_by(Events.event_start_date_and_time.desc()).all()
    if not events:
        return {"message": "No events found for this user."}
    
    provided_events_info = []
    for event in events:
        provided_events_info.append({
            "event_id": event.id,
            "event_title": event.event_title,
            "event_type": event.event_type,
            "event_provider_id": event.event_provider_id,
            "event_start_date_and_time": event.event_start_date_and_time,
            "event_lasting_time": event.event_duration_in_minutes,
            "event_location": event.event_location,
            "event_image": event.event_imageUrl,
            "event_description": event.event_description,
            "event_total_ticket_number": event.event_total_ticket_number,
            "event_remaining_ticket_number": event.event_remaining_ticket_number
        })
    return provided_events_info

