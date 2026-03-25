from fastapi import FastAPI, Depends, HTTPException, Body
from sqlmodel import Session, SQLModel, select
from typing import List, Optional
from database import init_db, get_session
from models import (
    User,
    Room,
    Reservation,
    Complaint,
    Dentist,
    DentalService,
    DentalAppointment,
)

app = FastAPI(title="Hotel Reservation API")


class RescheduleDentalAppointmentRequest(SQLModel):
    appointment_at: str
    dentist_id: Optional[int] = None
    service_id: Optional[int] = None
    notes: Optional[str] = None

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


@app.get("/users/lookup-by-phone", response_model=User)
def lookup_user_by_phone(phone: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.phone == phone)).first()
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
        # Fallback: Check if room_id was actually the room number (name)
        # Convert to string just in case, though room_id coming in is int
        room = session.exec(select(Room).where(Room.name == str(reservation.room_id))).first()
        
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    # Correct the room_id in the reservation object if we found it by name
    reservation.room_id = room.id
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

@app.get("/reservations/lookup", response_model=List[Reservation])
def lookup_reservations_by_email(email: str, session: Session = Depends(get_session)):
    # 1. Find User
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Find Reservations
    reservations = session.exec(select(Reservation).where(Reservation.user_id == user.id)).all()
    return reservations

@app.get("/reservations/{reservation_id}", response_model=Reservation)
def read_reservation(reservation_id: int, session: Session = Depends(get_session)):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@app.put("/reservations/{reservation_id}/cancel", response_model=Reservation)
def cancel_reservation(reservation_id: int, reason: str = Body(None, embed=True), session: Session = Depends(get_session)):
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


# --- Dentists ---
@app.post("/dentists", response_model=Dentist)
def create_dentist(dentist: Dentist, session: Session = Depends(get_session)):
    session.add(dentist)
    session.commit()
    session.refresh(dentist)
    return dentist


@app.get("/dentists", response_model=List[Dentist])
def read_dentists(active_only: bool = False, session: Session = Depends(get_session)):
    if active_only:
        dentists = session.exec(select(Dentist).where(Dentist.is_active == True)).all()
    else:
        dentists = session.exec(select(Dentist)).all()
    return dentists


@app.get("/dentists/{dentist_id}", response_model=Dentist)
def read_dentist(dentist_id: int, session: Session = Depends(get_session)):
    dentist = session.get(Dentist, dentist_id)
    if not dentist:
        raise HTTPException(status_code=404, detail="Dentist not found")
    return dentist


# --- Dental Services ---
@app.post("/dental-services", response_model=DentalService)
def create_dental_service(service: DentalService, session: Session = Depends(get_session)):
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@app.get("/dental-services", response_model=List[DentalService])
def read_dental_services(active_only: bool = False, session: Session = Depends(get_session)):
    if active_only:
        services = session.exec(select(DentalService).where(DentalService.is_active == True)).all()
    else:
        services = session.exec(select(DentalService)).all()
    return services


@app.get("/dental-services/{service_id}", response_model=DentalService)
def read_dental_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(DentalService, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Dental service not found")
    return service


# --- Dental Appointments ---
@app.post("/dental-appointments", response_model=DentalAppointment)
def create_dental_appointment(
    appointment: DentalAppointment, session: Session = Depends(get_session)
):
    user = session.get(User, appointment.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dentist = session.get(Dentist, appointment.dentist_id)
    if not dentist or not dentist.is_active:
        raise HTTPException(status_code=404, detail="Dentist not available")

    service = session.get(DentalService, appointment.service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Dental service not available")

    existing = session.exec(
        select(DentalAppointment).where(
            DentalAppointment.dentist_id == appointment.dentist_id,
            DentalAppointment.appointment_at == appointment.appointment_at,
            DentalAppointment.status == "scheduled",
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Dentist already has a scheduled appointment at this time",
        )

    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@app.get("/dental-appointments", response_model=List[DentalAppointment])
def read_dental_appointments(
    dentist_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(DentalAppointment)
    if dentist_id is not None:
        query = query.where(DentalAppointment.dentist_id == dentist_id)
    if user_id is not None:
        query = query.where(DentalAppointment.user_id == user_id)
    if status is not None:
        query = query.where(DentalAppointment.status == status)
    appointments = session.exec(query).all()
    return appointments


@app.get("/dental-appointments/availability")
def dental_appointment_availability(
    dentist_id: int, date: str, session: Session = Depends(get_session)
):
    dentist = session.get(Dentist, dentist_id)
    if not dentist or not dentist.is_active:
        raise HTTPException(status_code=404, detail="Dentist not available")

    scheduled = session.exec(
        select(DentalAppointment).where(
            DentalAppointment.dentist_id == dentist_id,
            DentalAppointment.status == "scheduled",
        )
    ).all()

    booked_slots = sorted(
        [a.appointment_at for a in scheduled if a.appointment_at.startswith(date)]
    )

    return {
        "dentist_id": dentist_id,
        "date": date,
        "booked_slots": booked_slots,
        "message": "Slots in booked_slots are unavailable for this dentist on the requested date.",
    }


@app.get("/dental-appointments/{appointment_id}", response_model=DentalAppointment)
def read_dental_appointment(appointment_id: int, session: Session = Depends(get_session)):
    appointment = session.get(DentalAppointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Dental appointment not found")
    return appointment


@app.put("/dental-appointments/{appointment_id}/cancel", response_model=DentalAppointment)
def cancel_dental_appointment(
    appointment_id: int, reason: str = Body(None, embed=True), session: Session = Depends(get_session)
):
    appointment = session.get(DentalAppointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Dental appointment not found")
    if appointment.status == "cancelled":
        return appointment
    appointment.status = "cancelled"
    if reason:
        if appointment.notes:
            appointment.notes = f"{appointment.notes}\nCancellation reason: {reason}"
        else:
            appointment.notes = f"Cancellation reason: {reason}"
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@app.put("/dental-appointments/{appointment_id}/complete", response_model=DentalAppointment)
def complete_dental_appointment(appointment_id: int, session: Session = Depends(get_session)):
    appointment = session.get(DentalAppointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Dental appointment not found")
    appointment.status = "completed"
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@app.put("/dental-appointments/{appointment_id}/reschedule", response_model=DentalAppointment)
def reschedule_dental_appointment(
    appointment_id: int,
    payload: RescheduleDentalAppointmentRequest,
    session: Session = Depends(get_session),
):
    appointment = session.get(DentalAppointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Dental appointment not found")
    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=400, detail="Cancelled appointments cannot be rescheduled"
        )

    new_dentist_id = payload.dentist_id or appointment.dentist_id
    new_service_id = payload.service_id or appointment.service_id

    dentist = session.get(Dentist, new_dentist_id)
    if not dentist or not dentist.is_active:
        raise HTTPException(status_code=404, detail="Dentist not available")

    service = session.get(DentalService, new_service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Dental service not available")

    conflict = session.exec(
        select(DentalAppointment).where(
            DentalAppointment.id != appointment.id,
            DentalAppointment.dentist_id == new_dentist_id,
            DentalAppointment.appointment_at == payload.appointment_at,
            DentalAppointment.status == "scheduled",
        )
    ).first()
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Dentist already has a scheduled appointment at this time",
        )

    appointment.appointment_at = payload.appointment_at
    appointment.dentist_id = new_dentist_id
    appointment.service_id = new_service_id
    appointment.status = "scheduled"
    if payload.notes is not None:
        appointment.notes = payload.notes

    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment
