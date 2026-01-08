from sqlmodel import Session, select
from database import engine
from models import User, Room, Reservation, Complaint

def inspect_data():
    with Session(engine) as session:
        print("--- ROOMS ---")
        rooms = session.exec(select(Room)).all()
        for r in rooms:
            print(f"ID: {r.id} | {r.name} ({r.type}) - ${r.price} | Available: {r.is_available}")
        
        print("\n--- USERS ---")
        users = session.exec(select(User)).all()
        for u in users:
            print(f"ID: {u.id} | {u.name} - {u.email}")

        print("\n--- RESERVATIONS ---")
        reservations = session.exec(select(Reservation)).all()
        for res in reservations:
            print(f"ID: {res.id} | User: {res.user_id} | Room: {res.room_id} | Status: {res.status}")

if __name__ == "__main__":
    inspect_data()
