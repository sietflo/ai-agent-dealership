#!/usr/bin/env python3
import argparse
import json
import os
import sys
from dotenv import load_dotenv
import warnings
from typing import Optional
load_dotenv()

from guardrails import GuardrailError, assert_tool_allowed, max_steps_instruction
from tracing import log_step, reset_log

_step_counter = 0


def _reset_steps(*args, **kwargs) -> None:
    global _step_counter
    _step_counter = 0

import os
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

_tool_executor = ThreadPoolExecutor(max_workers=4)


def _wrap_tool(name: str, fn):
    def inner(**kwargs):
        global _step_counter
        assert_tool_allowed(name)
        _step_counter += 1
        if _step_counter > int(os.getenv("MAX_AGENT_STEPS", "12")):
            raise GuardrailError("Max agent steps exceeded")

        timeout_seconds = int(os.getenv("TOOL_TIMEOUT_SECONDS", "10"))
        future = _tool_executor.submit(fn, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            log_step(_step_counter, name, kwargs, result)
            return json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
        except FutureTimeoutError:
            error_msg = f"Tool '{name}' timed out after {timeout_seconds}s"
            log_step(_step_counter, name, kwargs, None, error=error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
        except Exception as e:
            log_step(_step_counter, name, kwargs, None, error=str(e))
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    inner.__name__ = name
    return inner

def build_agent():
    try:
        from google.adk import Agent
    except ImportError:
        print("Install dependencies: pip install google-adk", file=sys.stderr)
        sys.exit(1)

    from .tools.api_dealership import (
        api_search_cars, api_get_car_details, api_create_car,
        api_search_customers, api_get_customer_history, api_create_customer,
        api_search_salesmen, api_get_salesman_stats, api_create_salesman,
        api_list_transactions, api_get_transaction_receipt, api_create_transaction,
        api_update_car, api_update_customer, api_update_salesman
    )

    def search_cars(status: str = None) -> str:
        """Search or list cars filtered by status (AVAILABLE, SOLD)."""
        return _wrap_tool("api_search_cars", api_search_cars)(status=status)

    def get_car_details(car_id: int) -> str:
        """Get full details of a specific car by ID."""
        return _wrap_tool("api_get_car_details", api_get_car_details)(car_id=car_id)

    def create_car(make: str, model: str, year: int, price: float, vin: str) -> str:
        """Create a new car listing in the dealership CRM."""
        return _wrap_tool("api_create_car", api_create_car)(make=make, model=model, year=year, price=price, vin=vin)

    def search_customers(query: str = None) -> str:
        """Search customers by name or email."""
        return _wrap_tool("api_search_customers", api_search_customers)(query=query)

    def get_customer_history(customer_id: int) -> str:
        """Get customer profile and history."""
        return _wrap_tool("api_get_customer_history", api_get_customer_history)(customer_id=customer_id)

    def create_customer(first_name: str, last_name: str, email: str, phone: str = None) -> str:
        """Onboard a new customer. Returns the customer object containing its ID."""
        return _wrap_tool("api_create_customer", api_create_customer)(
            first_name=first_name, last_name=last_name, email=email, phone=phone
        )

    def search_salesmen(name: str = None) -> str:
        """List or search salesmen by name."""
        return _wrap_tool("api_search_salesmen", api_search_salesmen)(name=name)

    def get_salesman_stats(salesman_id: int) -> str:
        """Get salesman profile by ID."""
        return _wrap_tool("api_get_salesman_stats", api_get_salesman_stats)(salesman_id=salesman_id)

    def create_salesman(first_name: str, last_name: str, email: str, phone: str = None) -> str:
        """Create a new salesman profile."""
        return _wrap_tool("api_create_salesman", api_create_salesman)(
            first_name=first_name, last_name=last_name, email=email, phone = phone
        )

    def list_transactions(customer_id: int = None) -> str:
        """List dealership sales transactions."""
        return _wrap_tool("api_list_transactions", api_list_transactions)(customer_id=customer_id)

    def get_transaction_receipt(transaction_id: int) -> str:
        """Get receipt details for a transaction."""
        return _wrap_tool("api_get_transaction_receipt", api_get_transaction_receipt)(transaction_id=transaction_id)

    def create_transaction(car_id: int, customer_id: int, salesman_id: int, sale_price: float) -> str:
        """Finalize a car sale transaction. Requires car_id, customer_id, salesman_id, and sale_price."""
        return _wrap_tool("api_create_transaction", api_create_transaction)(
            car_id=car_id, customer_id=customer_id, salesman_id=salesman_id, sale_price=sale_price
        )

    def update_car(car_id: int, make: Optional[str] = None, model: Optional[str] = None, price: Optional[float] = None, status: Optional[str] = None) -> str:
        """Update a car's make, model, price, or status."""
        return _wrap_tool("api_update_car", api_update_car)(car_id=car_id, make=make, model=model, price=price,
                                                            status=status)

    def update_customer(customer_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None,
                        phone: Optional[str] = None) -> str:
        """Update a customer's name, email, or phone number."""
        return _wrap_tool("api_update_customer", api_update_customer)(
            customer_id=customer_id, first_name=first_name, last_name=last_name, email=email, phone=phone
        )

    def update_salesman(salesman_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None,
                        phone: Optional[str] = None) -> str:
        """Update a salesman's name, email, or phone number."""
        return _wrap_tool("api_update_salesman", api_update_salesman)(
            salesman_id=salesman_id, first_name=first_name, last_name=last_name, email=email, phone=phone
        )

    tools = [
        search_cars, get_car_details, create_car,
        search_customers, get_customer_history, create_customer,
        search_salesmen, get_salesman_stats, create_salesman,
        list_transactions, get_transaction_receipt, create_transaction,
        update_car, update_salesman, update_customer
    ]

    instructions = (
            "You are an intelligent Car Dealership CRM Assistant. "
            "You can search, view, create, and update Cars, Customers, Salesmen, and Transactions.\n\n"

            "GENERAL WORKFLOW:\n"
            "The user will refer to people and cars by name, not by ID. Never ask the user for an ID — "
            "resolve names to IDs yourself using the search tools, and reuse the IDs returned by "
            "create/search/read calls in subsequent steps.\n\n"

            "SELLING A CAR (full deal):\n"
            "1. Find or onboard the customer.\n"
            "2. Find the specific available car requested (or the cheapest/first available if unspecified).\n"
            "3. Find or create the salesman.\n"
            "4. Finalize the transaction using the car_id, customer_id, and salesman_id from the steps above.\n\n"

            "HANDLING AMBIGUOUS MATCHES:\n"
            "If a search for a customer, car, or salesman returns more than one plausible match, "
            "do not guess. List the candidates you found and ask the user to clarify which one they mean.\n\n"

            "HANDLING DUPLICATES:\n"
            "If creating a customer or salesman fails because a record with that email already exists, "
            "do not treat it as a failure. Search for the existing record instead and continue the task "
            "using that record's ID.\n\n"

            "CAR CREATION:\n"
            "Never invent or guess a VIN. If the user wants to add a car and hasn't provided a VIN, "
            "ask them for it before calling the create tool.\n\n"

            "GENERAL:\n"
            "Never fabricate IDs, prices, employees, clients or other data not returned by a tool call. "
            "If a tool call fails for a reason other than a duplicate record, report the error to the user "
            "plainly instead of retrying blindly."
            + max_steps_instruction()
    )

    def _on_before_agent(callback_context):
        _reset_steps()

    return Agent(
        name="dealership_agent",
        model="gemini-2.5-flash",
        instruction=instructions,
        tools=tools,
        before_agent_callback= _on_before_agent,
    )


def run_once(agent, prompt: str, conversation: list | None):
    from google.adk import Runner
    _reset_steps()
    runner = Runner(agent=agent)

    # ADK handles input as a direct prompt string or session history
    input_text = prompt
    if conversation:
        input_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation]) + f"\nuser: {prompt}"

    response = runner.run(input_text)
    return str(response), None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?",
                        default="Onboard a new customer named Michael Scott (michael@dunder.com), find an available car, and sell it to him with salesman Bob.")
    args = parser.parse_args()

    reset_log()
    agent = build_agent()

    print("Running dealership agent...\n")
    answer, _ = run_once(agent, args.prompt, None)
    print("\n--- Final answer ---\n")
    print(answer)
    print(f"\nTrace written to agent/logs/trace.jsonl ({_step_counter} tool calls)")


root_agent = build_agent()

if __name__ == "__main__":
    main()