# ClassicModels API

A modular, production-style REST API built with **FastAPI** and **PostgreSQL**, based on the Classic Models sample database. The project covers database setup with Docker, a fully layered API architecture, customer CRUD endpoints, and a concurrent dashboard that fetches record counts from all 8 tables simultaneously using `asyncio`.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture: The 4 Layers](#architecture-the-4-layers)
- [Task 1 — PostgreSQL Setup with Docker](#task-1--postgresql-setup-with-docker)
- [Task 2 — Customer API Endpoints](#task-2--customer-api-endpoints)
- [Task 3 — Concurrency Dashboard](#task-3--concurrency-dashboard)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Logging](#logging)
- [Database Schema](#database-schema)

---

## Project Overview

This project was built in three tasks:

| Task | Description |
|------|-------------|
| **Task 1** | Set up a PostgreSQL database using Docker Compose, seeded with the Classic Models dataset |
| **Task 2** | Build a FastAPI application with full CRUD endpoints for the `customers` table using a 4-layer architecture |
| **Task 3** | Add 8 individual record-count endpoints and an aggregated `/overall_counts` dashboard using `asyncio.gather()` for concurrent database queries |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| **FastAPI** | Web framework for building the REST API |
| **SQLAlchemy** | ORM for database interaction (no raw SQL) |
| **Pydantic v2** | Data validation and request/response schemas |
| **PostgreSQL** | Relational database |
| **Docker Compose** | Container setup for the database |
| **python-dotenv** | Loading environment variables from `.env` |
| **uvicorn** | ASGI server to run FastAPI |
| **asyncio** | Python concurrency for parallel DB queries |

---

## Project Structure

```
week2_task1/
├── docker-compose.yml       # PostgreSQL container setup
├── seed.sql                 # Database schema + all data
├── .env                     # Environment variables (never commit this)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
├── main.py                  # FastAPI app entry point + logging config
├── database.py              # Layer 1 — DB connection & session
├── models.py                # SQLAlchemy ORM models (all 8 tables)
├── schemas.py               # Layer 2 — Pydantic validation schemas
├── crud.py                  # Layer 3 — All database operations
├── router.py                # Layer 4 — HTTP endpoints
└── app.log                  # Auto-generated log file (runtime)
```

---

## Architecture: The 4 Layers

The API is designed around a strict separation of concerns, inspired by the Twelve-Factor App methodology.

```
HTTP Request
     │
     ▼
┌─────────────┐
│  router.py  │  Layer 4 — Receives HTTP requests, calls crud, returns responses
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   crud.py   │  Layer 3 — All database logic (Create, Read, Update, Delete, Count)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  schemas.py │  Layer 2 — Pydantic models validate data before it touches the DB
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ database.py │  Layer 1 — Opens and closes the PostgreSQL connection
└─────────────┘
```

### Layer Responsibilities

**`database.py` — The Connection**
- Reads `DATABASE_URL` from the `.env` file
- Creates the SQLAlchemy engine and session factory
- Provides `get_db()` as a FastAPI dependency — opens a session per request, always closes it after
- Logs connection success or failure on startup

**`schemas.py` — The Blueprints**
- Defines three customer schemas: `CustomerCreate`, `CustomerOut`, `CustomerUpdate`
- `CustomerCreate` — used for new customers; validates all required fields
- `CustomerOut` — what the API returns; includes nested `orders` and `payments` lists
- `CustomerUpdate` — all fields are optional for partial updates (PATCH)
- Logs validation errors before they reach the database

**`crud.py` — The Kitchen**
- Never communicates with the internet or external services
- Uses SQLAlchemy ORM exclusively — no raw SQL strings
- Separate functions for Create, Read (single + list), Update, Delete
- 8 individual count functions, one per table
- Returns `None` or `False` on missing records; never raises database exceptions directly

**`router.py` — The Front Desk**
- Handles all HTTP methods: `GET`, `POST`, `PATCH`, `DELETE`
- Calls `crud.py` functions and translates results into HTTP responses
- Raises `HTTPException(404)` when `crud` returns `None`
- Contains the `async` `/overall_counts` endpoint using `asyncio.gather()`

---

## Task 1 — PostgreSQL Setup with Docker

### What was done
- Created a `docker-compose.yml` to run a PostgreSQL 15 container
- Used `seed.sql` to initialise all 8 tables and populate them with the Classic Models dataset
- Connected the FastAPI app to the container using environment variables

### Docker Compose Setup

```yaml
# docker-compose.yml (example structure)
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: classicmodels_user
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: modeldb
    ports:
      - "5432:5432"
    volumes:
      - ./seed.sql:/docker-entrypoint-initdb.d/seed.sql
```

### Starting the database

```bash
docker-compose up -d
```

---

## Task 2 — Customer API Endpoints

### What was done
- Built a full CRUD API for the `customers` table
- Used Pydantic for request validation and response shaping
- Related data (`orders`, `payments`) is returned nested inside each customer response
- Pagination via `skip` and `limit` query parameters
- Proper 404 error handling when a customer doesn't exist
- Logging at every layer

### Customer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/customers/` | List all customers (paginated) |
| `GET` | `/customers/{customerNumber}` | Get one customer with orders & payments |
| `POST` | `/customers/` | Create a new customer |
| `PATCH` | `/customers/{customerNumber}` | Partially update a customer |
| `DELETE` | `/customers/{customerNumber}` | Delete a customer |

### Pagination

```
GET /customers/?skip=0&limit=10
```

- `skip` — how many records to skip (default: `0`)
- `limit` — how many records to return, max `100` (default: `10`)

### Example Response — Single Customer

```json
{
  "customerNumber": 103,
  "customerName": "Atelier graphique",
  "contactLastName": "Schmitt",
  "contactFirstName": "Carine",
  "phone": "40.32.2555",
  "addressLine1": "54, rue Royale",
  "addressLine2": null,
  "city": "Nantes",
  "state": null,
  "postalCode": "44000",
  "country": "France",
  "salesRepEmployeeNumber": 1370,
  "creditLimit": "21000.00",
  "orders": [
    {
      "orderNumber": 10123,
      "orderDate": "2003-05-20",
      "requiredDate": "2003-05-29",
      "shippedDate": "2003-05-22",
      "status": "Shipped",
      "comments": null
    }
  ],
  "payments": [
    {
      "checkNumber": "HQ336336",
      "paymentDate": "2004-10-19",
      "amount": "6066.78"
    }
  ]
}
```

---

## Task 3 — Concurrency Dashboard

### What was done
- Added 8 individual `/table/count` endpoints (one per table)
- Built a single `/overall_counts` endpoint that fetches all 8 counts at the same time using `asyncio.gather()`
- Recorded and returned total response time in milliseconds
- Full logging of concurrency execution: when gather starts, when it completes, and how long it took

### Why Concurrency Matters

**Sequential approach (slow):**
```
query customers → wait 10ms
query orders    → wait 10ms
query products  → wait 10ms
...             → total: ~80ms
```

**Concurrent approach with `asyncio.gather()` (fast):**
```
query customers ──┐
query orders    ──┤
query products  ──┤ all run at the same time
...             ──┘
                  → total: ~10ms
```

### How it works

```python
await asyncio.gather(
    asyncio.to_thread(crud.count_customers,    db),
    asyncio.to_thread(crud.count_orders,       db),
    asyncio.to_thread(crud.count_products,     db),
    asyncio.to_thread(crud.count_employees,    db),
    asyncio.to_thread(crud.count_offices,      db),
    asyncio.to_thread(crud.count_payments,     db),
    asyncio.to_thread(crud.count_orderdetails, db),
    asyncio.to_thread(crud.count_productlines, db),
)
```

`asyncio.to_thread()` is used because SQLAlchemy's standard session is synchronous and blocking. Without it, running queries inside `gather()` would still execute sequentially on the event loop. `to_thread()` moves each blocking DB call into a thread pool so all 8 run in parallel.

### Individual Count Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/customers/count` | Total customers |
| `GET` | `/orders/count` | Total orders |
| `GET` | `/products/count` | Total products |
| `GET` | `/employees/count` | Total employees |
| `GET` | `/offices/count` | Total offices |
| `GET` | `/payments/count` | Total payments |
| `GET` | `/orderdetails/count` | Total order details |
| `GET` | `/productlines/count` | Total product lines |

### Aggregated Dashboard Endpoint

```
GET /overall_counts
```

**Example Response:**

```json
{
  "customers": 122,
  "orders": 326,
  "products": 110,
  "employees": 23,
  "offices": 7,
  "payments": 273,
  "orderdetails": 2996,
  "productlines": 7,
  "response_time_ms": 12.4
}
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- pip

### 1. Clone and enter the project

```bash
cd week2_task1
```

### 2. Start the database

```bash
docker-compose up -d
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your actual DB credentials
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the API

```bash
uvicorn main:app --reload
```

### 6. Open the interactive docs

```
http://localhost:8000/docs
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://classicmodels_user:your_password@localhost:5432/modeldb
```

> Never commit your `.env` file. It is listed in `.gitignore`.

---

## API Reference

All endpoints are documented interactively at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

### Tags

| Tag | Endpoints |
|-----|-----------|
| **Customers** | CRUD operations on the customers table |
| **Counts** | Individual record counts per table |
| **Dashboard** | Aggregated concurrent count endpoint |
| **Health** | `GET /` — basic health check |

### Health Check

```
GET /
```
```json
{ "status": "ok", "message": "Customer API is running." }
```

---

## Logging

Logging is implemented across all 4 layers. Logs are written to both the console and `app.log`.

### Log Format

```
2025-01-15 14:32:01 | INFO     | router   | 📥 GET /overall_counts — starting all 8 concurrent queries
2025-01-15 14:32:01 | INFO     | router   | ⚡ Launching asyncio.gather() for 8 concurrent DB queries...
2025-01-15 14:32:01 | INFO     | crud     | 📊 COUNT: Querying customers table.
2025-01-15 14:32:01 | INFO     | crud     | ✅ COUNT: customers = 122
2025-01-15 14:32:01 | INFO     | router   | ✅ asyncio.gather() completed in 12.4 ms
```

### What is logged

| Layer | Events Logged |
|-------|--------------|
| `database.py` | Connection success or failure, session open/close |
| `schemas.py` | Validation errors (empty fields, negative credit limits) |
| `crud.py` | Every query start and result, missing record warnings |
| `router.py` | Every incoming request, every response, all 404 errors, concurrency timing |

---

## Database Schema

The Classic Models database contains 8 tables:

```
productlines
    └── products
            └── orderdetails ──┐
                               │
offices                        │
    └── employees              │
            └── customers      │
                    ├── orders ─┘
                    └── payments
```

| Table | Rows | Primary Key |
|-------|------|-------------|
| `customers` | 122 | `customerNumber` |
| `orders` | 326 | `orderNumber` |
| `orderdetails` | 2,996 | `(orderNumber, productCode)` |
| `payments` | 273 | `(customerNumber, checkNumber)` |
| `products` | 110 | `productCode` |
| `productlines` | 7 | `productLine` |
| `employees` | 23 | `employeeNumber` |
| `offices` | 7 | `officeCode` |