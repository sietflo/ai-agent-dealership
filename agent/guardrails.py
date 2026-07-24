import os

class GuardrailError(Exception):
    """Raised when a guardrail rule is violated."""
    pass

# Explicit tool allowlist
ALLOWED_TOOLS = {
    # Cars
    "api_search_cars", "api_get_car_details", "api_create_car",
    # Customers
    "api_search_customers", "api_get_customer_history", "api_create_customer",
    # Salesmen
    "api_search_salesmen", "api_get_salesman_stats", "api_create_salesman",
    # Transactions
    "api_list_transactions", "api_get_transaction_receipt", "api_create_transaction",
    # Updating
    "api_update_car", "api_update_customer", "api_update_salesman"
}

def assert_tool_allowed(tool_name: str) -> None:
    if tool_name not in ALLOWED_TOOLS:
        raise GuardrailError(f"Tool '{tool_name}' is not in the allowed tools list.")

def max_steps_instruction() -> str:
    max_steps = os.getenv("MAX_AGENT_STEPS", "12")
    return f" Do not take more than {max_steps} tool steps total."