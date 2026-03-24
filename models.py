from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    email: Optional[str] = None

class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g. "Room 101"
    type: str  # e.g. "Single", "Double", "Suite"
    price: float
    is_available: bool = True

class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="room.id")
    check_in: str # Keeping simple as ISO strings
    check_out: str
    status: str = "confirmed" # confirmed, cancelled

class Complaint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    details: str
    status: str = "open" # open, resolved


class Dentist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    specialty: str = "General Dentistry"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True


class DentalService(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    duration_minutes: int = 30
    price: float = 0.0
    description: Optional[str] = None
    is_active: bool = True


class DentalAppointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    dentist_id: int = Field(foreign_key="dentist.id")
    service_id: int = Field(foreign_key="dentalservice.id")
    appointment_at: str  # ISO datetime string
    notes: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, cancelled
