from sqlmodel import Session, select
from database import engine
from models import Room

def seed_rooms():
    with Session(engine) as session:
        # Define all rooms we want to ensure exist
        rooms_data = [
            {"name": "101", "type": "Single", "price": 100.0},
            {"name": "102", "type": "Double", "price": 150.0},
            {"name": "103", "type": "Single", "price": 100.0},
            {"name": "201", "type": "Suite", "price": 300.0},
            {"name": "202", "type": "Suite", "price": 300.0},
            {"name": "203", "type": "Double", "price": 160.0},
            {"name": "301", "type": "Penthouse", "price": 500.0},
            {"name": "302", "type": "Single", "price": 110.0},
            {"name": "401", "type": "Double", "price": 155.0},
            {"name": "402", "type": "Suite", "price": 320.0},
        ]

        count = 0
        print("Checking and seeding rooms...")
        for r_data in rooms_data:
            # Check if this specific room name exists
            existing = session.exec(select(Room).where(Room.name == r_data["name"])).first()
            if not existing:
                room = Room(**r_data, is_available=True)
                session.add(room)
                count += 1
                print(f"Added room {r_data['name']}")
        
        session.commit()
        if count == 0:
            print("All rooms already exist.")
        else:
            print(f"Successfully added {count} new rooms.")

if __name__ == "__main__":
    seed_rooms()
