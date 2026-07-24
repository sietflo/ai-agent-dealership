from ..client import api_client

# --- CARS ---
def api_search_cars(status: str = None) -> list:
    params = {"status": status} if status else {}
    return api_client.request("GET", "/cars/", params=params)

def api_get_car_details(car_id: int) -> dict:
    return api_client.request("GET", f"/cars/{car_id}")

def api_create_car(make: str, model: str, year: int, price: float, vin: str) -> dict:
    payload = {"make": make, "model": model, "year": year, "price": price, "vin": vin}
    return api_client.request("POST", "/cars/", json=payload)

# --- CUSTOMERS ---
def api_search_customers(query: str = None) -> list:
    params = {"query": query} if query else {}
    return api_client.request("GET", "/customers/", params=params)

def api_get_customer_history(customer_id: int) -> dict:
    return api_client.request("GET", f"/customers/{customer_id}")

def api_create_customer(first_name: str, last_name: str, email: str, phone: str = None) -> dict:
    payload = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone}
    return api_client.request("POST", "/customers/", json=payload)
# --- SALESMEN ---
def api_search_salesmen(name: str = None) -> list:
    params = {"name": name} if name else {}
    return api_client.request("GET", "/salesmen/", params=params)

def api_get_salesman_stats(salesman_id: int) -> dict:
    return api_client.request("GET", f"/salesmen/{salesman_id}")

def api_create_salesman(first_name: str, last_name: str, email: str, phone: str=None) -> dict:
    payload = {"first_name": first_name, "last_name": last_name, "email": email, "phone": phone}
    return api_client.request("POST", "/salesmen/", json=payload)
# --- TRANSACTIONS ---
def api_list_transactions(customer_id: int = None) -> list:
    params = {"customer_id": customer_id} if customer_id else {}
    return api_client.request("GET", "/transactions/", params=params)

def api_get_transaction_receipt(transaction_id: int) -> dict:
    return api_client.request("GET", f"/transactions/{transaction_id}")

def api_create_transaction(car_id: int, customer_id: int, salesman_id: int, sale_price: float) -> dict:
    payload = {"car_id": car_id, "customer_id": customer_id, "salesman_id": salesman_id, "sale_price": sale_price}
    return api_client.request("POST", "/transactions/", json=payload)