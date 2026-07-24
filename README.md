# Car Dealership CRM Agent

An AI agent (Google ADK + Gemini) that manages a car dealership's cars, customers,
salesmen, and transactions through a real FastAPI + PostgreSQL backend. The agent
resolves names to database IDs on its own — the user never needs to know or supply
internal IDs.

## Architecture

```
User prompt
   │
   ▼
agent/agent.py          ADK Agent + tool wrappers (search, read, create, update)
   │  each call goes through:
   │  - guardrails.py   (allowlist, max steps)
   │  - tracing.py      (logs every call to logs/trace.jsonl)
   │  - timeout wrapper (ThreadPoolExecutor, default 10s per tool call)
   ▼
agent/tools/api_dealership.py   Domain functions, one per API operation
   ▼
agent/client.py          Authenticated HTTP client (login → Bearer token)
   ▼
api/                      FastAPI app → PostgreSQL (real DB, not mocked)
```

## Prerequisites

- Python 3.10+
- Docker (for PostgreSQL)
- A Gemini API key

## Setup

1. **Start the database:**
   ```bash
   docker compose up -d
   ```

2. **Install dependencies** (in both `api/` and `agent/` virtual environments, or one shared venv):
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables.**

   `api/.env`:
   ```
   DATABASE_URL=postgresql+psycopg://crm_admin:<password>@localhost:5432/dealership_db
   ```

   `agent/.env`:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   API_BASE_URL=http://localhost:8000
   AGENT_USERNAME=admin
   AGENT_PASSWORD=admin123
   MAX_AGENT_STEPS=12
   TOOL_TIMEOUT_SECONDS=10
   ```

4. **Run database migrations:**
   ```bash
   cd api
   alembic upgrade head
   ```

5. **Seed sample data** (2 salesmen, 2 customers, 4 cars, 1 transaction):
   ```bash
   python -m app.seed
   ```

6. **Start the API:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Swagger docs available at `http://localhost:8000/docs`.

## Running the Agent

From the `agent/` folder:

```bash
adk run .
```

This starts an interactive session. Type a request; type `exit` to quit.

## Guardrails

- **Max steps**: agent stops after `MAX_AGENT_STEPS` tool calls in a single turn (default 12).
- **Tool allowlist**: only explicitly listed tools in `guardrails.py` may execute.
- **Timeout**: each tool call is bounded by `TOOL_TIMEOUT_SECONDS` (default 10s) via a
  `ThreadPoolExecutor`; a timed-out call returns an error to the agent instead of hanging.
- **No fabrication**: the agent is instructed never to invent IDs, VINs, prices, or other
  data not returned by a tool call, and to report errors plainly rather than guessing.
- **Ambiguous matches**: if a search returns multiple plausible matches, the agent lists
  the candidates and asks the user to clarify instead of picking one at random.
- **Duplicate handling**: if creating a customer or salesman fails because the email
  already exists, the agent looks up the existing record instead of failing the task.

## Trace Logging

Every tool call (success or failure) is appended to `agent/logs/trace.jsonl` as a JSON
line containing a timestamp, the tool name, its arguments, its result, and any error.

## Sample Queries

**1. Full sale in one request:**
```
Onboard a new customer named Michael Scott (michael@dunder.com, phone 555-0100),
find an available car, and sell it to him with salesman Bob.
```
Expected flow: create customer → search available cars → search/find salesman →
create transaction, all chained automatically using the IDs returned at each step.

**2. Update + guardrail check:**
```
Update the Ford Mustang's price to $32,000. Then update Jane Miller's phone number
to 555-9999. Finally, try to update car ID 999, which doesn't exist, and tell me
what happens.
```
Expected flow: two successful updates, followed by a clean reported error (404 Not
Found) for the nonexistent car — the agent should not crash or fabricate a result.

## Project Structure

```
car_dealer_agent/
├── api/                  FastAPI backend
│   ├── alembic/          Database migrations
│   └── app/
│       ├── models.py     SQLAlchemy models
│       ├── schemas.py    Pydantic schemas
│       ├── routers/      cars, customers, salesmen, transactions, auth
│       └── seed.py        Sample data
└── agent/                 ADK agent
    ├── agent.py            Agent definition, tool wrappers, guardrail wiring
    ├── client.py            Authenticated API client
    ├── guardrails.py        Allowlist + step-limit helper
    ├── tracing.py            Trace logging
    ├── tools/
    │   └── api_dealership.py  One function per API endpoint
    └── logs/
        └── trace.jsonl        Generated at runtime
```