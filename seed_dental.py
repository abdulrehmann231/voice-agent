from sqlmodel import Session, select
from database import engine, init_db
from models import Dentist, DentalService


def seed_dentists_and_services():
    # Ensure tables exist before seeding.
    init_db()

    dentists_data = [
        {
            "name": "Dr. Sarah Ahmed",
            "specialty": "General Dentistry",
            "phone": "+1-555-0101",
            "email": "sarah.ahmed@clinic.com",
            "is_active": True,
        },
        {
            "name": "Dr. Michael Lee",
            "specialty": "Orthodontics",
            "phone": "+1-555-0102",
            "email": "michael.lee@clinic.com",
            "is_active": True,
        },
        {
            "name": "Dr. Priya Nair",
            "specialty": "Endodontics",
            "phone": "+1-555-0103",
            "email": "priya.nair@clinic.com",
            "is_active": True,
        },
    ]

    services_data = [
        {
            "name": "Dental Checkup",
            "duration_minutes": 30,
            "price": 50.0,
            "description": "Routine oral health examination and consultation.",
            "is_active": True,
        },
        {
            "name": "Teeth Cleaning",
            "duration_minutes": 45,
            "price": 80.0,
            "description": "Professional scaling and polishing.",
            "is_active": True,
        },
        {
            "name": "Tooth Filling",
            "duration_minutes": 60,
            "price": 120.0,
            "description": "Cavity treatment with composite filling.",
            "is_active": True,
        },
        {
            "name": "Root Canal",
            "duration_minutes": 90,
            "price": 350.0,
            "description": "Root canal therapy for infected tooth pulp.",
            "is_active": True,
        },
        {
            "name": "Braces Consultation",
            "duration_minutes": 40,
            "price": 70.0,
            "description": "Orthodontic evaluation and treatment planning.",
            "is_active": True,
        },
    ]

    with Session(engine) as session:
        dentist_count = 0
        service_count = 0

        print("Checking and seeding dentists...")
        for dentist_data in dentists_data:
            existing_dentist = session.exec(
                select(Dentist).where(Dentist.email == dentist_data["email"])
            ).first()
            if not existing_dentist:
                session.add(Dentist(**dentist_data))
                dentist_count += 1
                print(f"Added dentist: {dentist_data['name']}")

        print("Checking and seeding dental services...")
        for service_data in services_data:
            existing_service = session.exec(
                select(DentalService).where(DentalService.name == service_data["name"])
            ).first()
            if not existing_service:
                session.add(DentalService(**service_data))
                service_count += 1
                print(f"Added service: {service_data['name']}")

        session.commit()

        if dentist_count == 0:
            print("All dentists already exist.")
        else:
            print(f"Successfully added {dentist_count} new dentists.")

        if service_count == 0:
            print("All dental services already exist.")
        else:
            print(f"Successfully added {service_count} new dental services.")


if __name__ == "__main__":
    seed_dentists_and_services()
