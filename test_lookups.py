from sqlmodel import Session, select
from database import engine
from models import User, Reservation

def verify_lookups():
    with Session(engine) as session:
        # 1. Setup Data for testing
        print("Setting up test data...")
        # Ensure user exists
        test_email = "lookup@test.com"
        user = session.exec(select(User).where(User.email == test_email)).first()
        if not user:
            user = User(name="Lookup Test", phone="555", email=test_email)
            session.add(user)
            session.commit()
            session.refresh(user)
        print(f"User created/found: {user.email} (ID: {user.id})")

        # 2. Simulate User Lookup by Email (effectively what the API does)
        found_user = session.exec(select(User).where(User.email == test_email)).first()
        if found_user and found_user.id == user.id:
             print("SUCCESS: User lookup by email verified (DB Logic).")
        else:
             print("FAILURE: User lookup by email failed.")

        # 3. Simulate Reservation Lookup by ID
        # Create a dummy reservation if needed, but simplified check:
        # Just creating one to be sure
        from models import Room
        room = session.exec(select(Room)).first() # grab any room
        if not room:
            print("No rooms found, skipping reservation test.")
            return

        res = Reservation(user_id=user.id, room_id=room.id, check_in="2025-01-01", check_out="2025-01-02", status="confirmed")
        session.add(res)
        session.commit()
        session.refresh(res)
        print(f"Reservation created: ID {res.id}")

        # Lookup
        found_res = session.get(Reservation, res.id)
        if found_res and found_res.id == res.id:
             print("SUCCESS: Reservation lookup by ID verified (DB Logic).")
        else:
             print("FAILURE: Reservation lookup by ID failed.")

if __name__ == "__main__":
    verify_lookups()
