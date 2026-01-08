from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app, get_session
import pytest

# Use SQLite for testing to avoid needing a running Postgres
sqlite_file_name = "test_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)

def test_workflow():
    create_db_and_tables()
    
    # 1. Create Data
    # Create User
    user_resp = client.post("/users", json={"name": "Alice", "phone": "1234567890", "email": "alice@example.com"})
    assert user_resp.status_code == 200
    user_data = user_resp.json()
    assert user_data["name"] == "Alice"
    user_id = user_data["id"]

    # Create Room
    room_resp = client.post("/rooms", json={"name": "101", "type": "Single", "price": 100.0, "is_available": True})
    assert room_resp.status_code == 200
    room_data = room_resp.json()
    room_id = room_data["id"]

    # 2. Check Availability
    rooms_resp = client.get("/rooms?available_only=true")
    assert len(rooms_resp.json()) >= 1

    # 3. Create Reservation
    res_resp = client.post("/reservations", json={
        "user_id": user_id,
        "room_id": room_id,
        "check_in": "2023-10-27",
        "check_out": "2023-10-28"
    })
    assert res_resp.status_code == 200
    res_data = res_resp.json()
    assert res_data["status"] == "confirmed"
    res_id = res_data["id"]

    # 4. Check Room is now unavailable
    rooms_resp_after = client.get("/rooms?available_only=true")
    # Should not find the room we just booked (assuming clean db or unique room)
    # Since we use a file db, it persists across runs if not deleted, but for this flow it's fine.
    # We can filter to see if OUR room is there.
    available_ids = [r["id"] for r in rooms_resp_after.json()]
    assert room_id not in available_ids

    # 5. Create Complaint
    comp_resp = client.post("/complaints", json={"user_id": user_id, "details": "AC not working"})
    assert comp_resp.status_code == 200
    assert comp_resp.json()["status"] == "open"
    
    print("Verification Successful!")

if __name__ == "__main__":
    try:
        test_workflow()
    except AssertionError as e:
        print(f"Verification Failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
