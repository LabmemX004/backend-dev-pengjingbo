import smtplib
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.orm import Session
from ..blueprint.dbBlueprint import SessionLocal, Booking_ticket_action_info, Events, Users
from ..auth.jwt_bearer import jwtBearer, get_current_user
import os
import uuid


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingTicketData(BaseModel):
    event_id: int
    number_of_tickets: int  
    user_id: int  

@router.post("/bookTicket", dependencies=[Depends(jwtBearer())])
def book_ticket(booking_data: BookingTicketData, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)): 
  
  print(booking_data.user_id)
  try:
    event = db.query(Events).filter(Events.id == booking_data.event_id).first()
    user = db.query(Users).filter(Users.id == booking_data.user_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.event_remaining_ticket_number < booking_data.number_of_tickets:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    if(int(current_user["user_id"]) != booking_data.user_id):
        raise HTTPException(status_code=403, detail="User ID does not match the token")
    ticket_code_unique = (f"TICKET-{event.event_start_date_and_time.strftime('%Y%m%d%H%M')}-{uuid.uuid4()}")
    booking = Booking_ticket_action_info(
        user_id=current_user["user_id"],
        event_id=booking_data.event_id,
        number_of_tickets=booking_data.number_of_tickets,
        status="Booked",
        ticket_code = ticket_code_unique
    )
    event.event_remaining_ticket_number -= booking_data.number_of_tickets
    db.add(booking)
    reciverEmail = user.email
    subject = f"Your ticket booking is successful, here is the detial information of event: {event.event_title}"
    body = f"Event: {event.event_title}\nDate and Time: {event.event_start_date_and_time}\nLocation: {event.event_location}\nNumber of Tickets: {booking_data.number_of_tickets}\n\nYour ticket code is:{ticket_code_unique}\n\nThank you for booking with us!"
    message = f"Subject: {subject}\n\n{body}"
    
    try:
        sever = smtplib.SMTP('smtp.gmail.com', 587)
        sever.starttls()
        sever.login(os.getenv("emailSender"), os.getenv("emailPassword"))
        sever.sendmail(os.getenv("emailSender"), reciverEmail, message)
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        sever.quit()
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  db.commit()
  db.refresh(booking)
  return {"status": "SuccessfullyBookedTicket", "booking_id": booking.user_id}
