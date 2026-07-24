# api/app/seed.py
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Car, Customer, Salesman, Transaction


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        db.query(Transaction).delete()
        db.query(Car).delete()
        db.query(Customer).delete()
        db.query(Salesman).delete()
        db.commit()

        salesman1 = Salesman(first_name="Alice", last_name="Vance", email="alice@dealership.com", phone = "222-0101")
        salesman2 = Salesman(first_name="Bob", last_name="Smith", email="bob@dealership.com", phone = "222-0101")
        db.add_all([salesman1, salesman2])
        db.commit()

        customer1 = Customer(first_name="John", last_name="Doe", email="johndoe@gmail.com", phone="555-0101")
        customer2 = Customer(first_name="Jane", last_name="Miller", email="jane.m@gmail.com", phone="555-0102")
        db.add_all([customer1, customer2])
        db.commit()

        car1 = Car(vin="1HGCR2F83HA123456", make="Toyota", model="Camry", year=2022, price=24500.0, status="SOLD")
        car2 = Car(vin="2T1BR3HE4KC654321", make="Honda", model="Civic", year=2023, price=26000.0, status="AVAILABLE")
        car3 = Car(vin="1FA6P8CF0R5789012", make="Ford", model="Mustang", year=2024, price=35000.0, status="AVAILABLE")
        car4 = Car(vin="5YJ3E1EA7KF345678", make="Tesla", model="Model 3", year=2023, price=42000.0, status="RESERVED")
        db.add_all([car1, car2, car3, car4])
        db.commit()

        tx1 = Transaction(
            car_id=car1.id,
            customer_id=customer1.id,
            salesman_id=salesman1.id,
            sale_price=24000.0,
            created_at=datetime.now() - timedelta(days=5)
        )
        db.add(tx1)
        db.commit()

        print("✅ Database successfully seeded!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()