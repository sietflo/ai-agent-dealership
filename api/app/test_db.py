# test_db.py
from database import engine, Base, SessionLocal
from models import Salesman, Customer, Car, Transaction


def verify_setup():
    print("1. Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("2. Inserting dummy records...")
        salesman = Salesman(first_name="Alice", last_name="Smith", email="alice@dealership.com")
        customer = Customer(first_name="Bob", last_name="Jones", email="bob@gmail.com")
        car = Car(vin="1HGCR2F83HA000000", make="Honda", model="Accord", price=25000.00)

        db.add_all([salesman, customer, car])
        db.commit()  # Saves them to give them IDs

        # Mark car as SOLD and log the transaction
        car.status = "SOLD"
        txn = Transaction(
            car_id=car.id,
            customer_id=customer.id,
            salesman_id=salesman.id,
            sale_price=24000.00
        )
        db.add(txn)
        db.commit()

        print("\n3. Querying database back to verify relationships...")
        saved_txn = db.query(Transaction).first()

        print("\n--- TEST SUCCESSFUL ---")
        print(f"Transaction ID : {saved_txn.id}")
        print(f"Sold Car       : {saved_txn.car.make} {saved_txn.car.model} (VIN: {saved_txn.car.vin})")
        print(f"Sold To        : {saved_txn.customer.first_name} {saved_txn.customer.last_name}")
        print(f"Sold By        : {saved_txn.salesman.first_name} {saved_txn.salesman.last_name}")
        print(f"Final Price    : ${saved_txn.sale_price}")
        print("-----------------------\n")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    verify_setup()