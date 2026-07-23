# api/app/seed.py
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Car, Customer, Salesman, Transaction


def seed_data():
    # 1. Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # 2. Clear existing data (optional, but prevents duplicate keys on rerun)
        db.query(Transaction).delete()
        db.query(Car).delete()
        db.query(Customer).delete()
        db.query(Salesman).delete()
        db.commit()

        # 3. Create Salesmen
        salesman1 = Salesman(first_name="Alice", last_name = "Vance", email="alice@dealership.com")
        salesman2 = Salesman(first_name="Bob", last_name = "Smith", email="bob@dealership.com")
        db.add_all([salesman1, salesman2])
        db.commit()

        # 4. Create Customers
        customer1 = Customer(first_name="John", last_name = "Doe", email="johndoe@gmail.com")
        customer2 = Customer(first_name="Jane", last_name = "Miller", email="jane.m@gmail.com")
        db.add_all([customer1, customer2])
        db.commit()

        # 5. Create Cars
        car1 = Car(vin="1HGCR2F83HA123456", make="Toyota", model="Camry", price=24500.0, status="sold")
        car2 = Car(vin="2T1BR3HE4KC654321", make="Honda", model="Civic", price=26000.0, status="available")
        car3 = Car(vin="1FA6P8CF0R5789012", make="Ford", model="Mustang", price=35000.0, status="available")
        car4 = Car(vin="5YJ3E1EA7KF345678", make="Tesla", model="Model 3", price=42000.0, status="reserved")
        db.add_all([car1, car2, car3, car4])
        db.commit()

        # 6. Create Transactions
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