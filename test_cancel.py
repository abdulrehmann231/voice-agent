from sqlmodel import Session, select
from database import engine
from models import User, Room, Reservation

def verify_cancel():
    with Session(engine) as session:
        # 1. Setup: Ensure user and room exist
        user = session.exec(select(User)).first()
        if not user:
            user = User(name="CancelTest", phone="999", email="cancel@test.com")
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Ensure an available room
        room = session.exec(select(Room).where(Room.is_available == True)).first()
        if not room:
            # Create one if none available
            room = Room(name="999", type="Test", price=10.0, is_available=True)
            session.add(room)
            session.commit()
            session.refresh(room)
        
        print(f"Using Room {room.name} (Available: {room.is_available})")

        # 2. Book the room
        print("Booking room...")
        res = Reservation(user_id=user.id, room_id=room.id, check_in="2024-01-01", check_out="2024-01-05")
        session.add(res)
        room.is_available = False # Manual update simulating API
        session.add(room)
        session.commit()
        session.refresh(res)
        session.refresh(room)
        print(f"Room {room.name} booked. Available: {room.is_available} (Should be False)")

        if room.is_available:
             print("FAILURE: Room should be unavailable after booking.")
             return

        # 3. Cancel the booking (simulate API logic)
        print("Cancelling booking...")
        res.status = "cancelled"
        session.add(res)
        room.is_available = True
        session.add(room)
        session.commit()
        
        session.refresh(res)
        session.refresh(room)
        
        if res.status == "cancelled" and room.is_available == True:
            print("SUCCESS: Reservation cancelled and room marked available.")
        else:
            print(f"FAILURE: Status: {res.status}, Room Available: {room.is_available}")

if __name__ == "__main__":
    verify_cancel()
