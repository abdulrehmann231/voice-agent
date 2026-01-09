from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from database import init_db, get_session
from models import User, Room, Reservation, Complaint

app = FastAPI(title="Hotel Reservation API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Hotel Reservation API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Users ---
@app.post("/users", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/lookup", response_model=User)
def lookup_user(email: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Rooms ---
@app.post("/rooms", response_model=Room)
def create_room(room: Room, session: Session = Depends(get_session)):
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

@app.get("/rooms", response_model=List[Room])
def read_rooms(available_only: bool = False, session: Session = Depends(get_session)):
    if available_only:
        rooms = session.exec(select(Room).where(Room.is_available == True)).all()
    else:
        rooms = session.exec(select(Room)).all()
    return rooms

# --- Reservations ---
@app.post("/reservations", response_model=Reservation)
def create_reservation(reservation: Reservation, session: Session = Depends(get_session)):
    # Check if room is available (basic check)
    room = session.get(Room, reservation.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.is_available:
         raise HTTPException(status_code=400, detail="Room is not available")
    
    # Check User
    user = session.get(User, reservation.user_id)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    
    session.add(reservation)
    
    # Mark room as unavailable
    room.is_available = False
    session.add(room)
    
    session.commit()
    session.refresh(reservation)
    return reservation

@app.get("/reservations/{reservation_id}", response_model=Reservation)
def read_reservation(reservation_id: int, session: Session = Depends(get_session)):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@app.put("/reservations/{reservation_id}/cancel", response_model=Reservation)
def cancel_reservation(reservation_id: int, reason: str = Body(None), session: Session = Depends(get_session)):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if reservation.status == "cancelled":
        return reservation # Already cancelled

    # Update reservation status
    reservation.status = "cancelled"
    session.add(reservation)

    # Free up the room
    room = session.get(Room, reservation.room_id)
    if room:
        room.is_available = True
        session.add(room)
    
    session.commit()
    session.refresh(reservation)
    return reservation

# --- Complaints ---
@app.post("/complaints", response_model=Complaint)
def create_complaint(complaint: Complaint, session: Session = Depends(get_session)):
    session.add(complaint)
    session.commit()
    session.refresh(complaint)
    return complaint

@app.get("/complaints", response_model=List[Complaint])
def read_complaints(session: Session = Depends(get_session)):
    complaints = session.exec(select(Complaint)).all()
    return complaints
