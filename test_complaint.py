from sqlmodel import Session, select
from database import engine
from models import User, Complaint
import random

def verify_complaints():
    with Session(engine) as session:
        # 1. Ensure a user exists to complain
        user = session.exec(select(User)).first()
        if not user:
            print("Creating a dummy user for complaint test...")
            user = User(name="Complainer", phone="000", email="complaint@test.com")
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # 2. Create a complaint
        print(f"User {user.name} is filing a complaint...")
        complaint_text = f"The Wi-Fi is slow #{random.randint(1000,9999)}"
        new_complaint = Complaint(user_id=user.id, details=complaint_text)
        session.add(new_complaint)
        session.commit()
        session.refresh(new_complaint)
        print(f"Complaint filed with ID: {new_complaint.id}")

        # 3. Read it back
        saved_complaint = session.get(Complaint, new_complaint.id)
        if saved_complaint and saved_complaint.details == complaint_text:
            print("SUCCESS: Complaint was saved and retrieved correctly.")
            print(f"Details: {saved_complaint.details}")
            print(f"Status: {saved_complaint.status}")
        else:
            print("FAILURE: Could not retrieve the complaint correctly.")

if __name__ == "__main__":
    verify_complaints()
