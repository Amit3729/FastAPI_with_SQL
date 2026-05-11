import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import asyncio
import time

import crud
import schemas
from database import get_db, SessionLocal

logger = logging.getLogger(__name__)

# ── Customer CRUD Router (prefix: /customers) ─────────────────────────────────
router = APIRouter(prefix="/customers", tags=["Customers"])


# GET /customers — paginated list
@router.get("/", response_model=List[schemas.CustomerOut])
def list_customer(
    skip:  int = Query(default=0,  ge=0,  description="Records to skip (offset)"),
    limit: int = Query(default=10, ge=1, le=100, description="Max records to return"),
    db:    Session = Depends(get_db),
):
    """
    Returns a paginated list of customers.
 
    - **skip**: how many records to skip (e.g. skip=20 → start at record 21)
    - **limit**: how many records per page (max 100)
    """
    logger.info("GET /customers — skip=%d, limit=%d", skip, limit)
    customers = crud.get_customers(db, skip=skip, limit=limit)
    logger.info("GET /customers — returning %d record(s)", len(customers))
    return customers


# GET /customers/{customerNumber} — single customer with related data
@router.get("/{customer_number}", response_model=schemas.CustomerOut)
def get_customer(customer_number: int, db: Session = Depends(get_db)):
    """Returns a single customer including their orders and payments.
 
    - Returns **404** if the customer number does not exist.
    - Orders and payments are returned as nested lists (empty list if none)."""
    logger.info("GET /customers/%d", customer_number)
    customer = crud.get_customer(db, customer_number)

    if customer is None:
        logger.warning("GET /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")
    logger.info("GET /customers/%d — found customer '%s'", customer_number, customer.customerName)
    return customer


# POST /customers — create a new customer
@router.post("/", response_model=schemas.CustomerOut, status_code=201)
def create_customer(customer_data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Creates a new customer. The database auto-assigns the customerNumber.
 
    - Pydantic validates all fields before the DB is touched.
    - Returns the created customer with its new ID."""
    logger.info("POST /customers — creating customer '%s'", customer_data.customerName)
    new_customer = crud.create_customer(db, customer_data)
    logger.info("POST /customers — created customer #%d", new_customer.customerNumber)
    return new_customer


# PATCH /customers/{customerNumber} — partial update
@router.patch("/{customer_number}", response_model=schemas.CustomerOut)
def update_customer(
    customer_number: int,
    update_data: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
):
    """Partially updates a customer. Only send the fields you want to change.
 
    - Returns **404** if the customer number does not exist."""
    logger.info("PATCH /customers/%d — updating customer", customer_number)
    updated = crud.update_customer(db, customer_number, update_data)

    if updated is None:
        logger.warning("PATCH /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")

    logger.info("PATCH /customers/%d — updated successfully", customer_number)
    return updated


# DELETE /customers/{customerNumber}
@router.delete("/{customer_number}", status_code=204)
def delete_customer(customer_number: int, db: Session = Depends(get_db)):
    """Deletes a customer by ID.
 
    - Returns **204 No Content** on success.
    - Returns **404** if the customer number does not exist."""
    logger.info("DELETE /customers/%d — deleting customer", customer_number)
    deleted = crud.delete_customer(db, customer_number)

    if not deleted:
        logger.warning("DELETE /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")
    logger.info("DELETE /customers/%d — deleted successfully", customer_number)


# ── Count Endpoints (separate router — NO prefix) ─────────────────────────────
# Paths: /customers/count, /orders/count, … , /overall_counts
counts_router = APIRouter(tags=["Counts"])


@counts_router.get("/customers/count")
def get_customer_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the customers table."""
    logger.info("GET /customers/count")
    count = crud.count_customers(db)
    logger.info("GET /customers/count — %d", count)
    return {"table": "customers", "count": count}


@counts_router.get("/orders/count")
def get_order_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the orders table."""
    logger.info("GET /orders/count")
    count = crud.count_orders(db)
    logger.info("GET /orders/count — %d", count)
    return {"table": "orders", "count": count}


@counts_router.get("/products/count")
def get_product_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the products table."""
    logger.info("GET /products/count")
    count = crud.count_products(db)
    logger.info("GET /products/count — %d", count)
    return {"table": "products", "count": count}


@counts_router.get("/employees/count")
def get_employee_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the employees table."""
    logger.info("GET /employees/count")
    count = crud.count_employees(db)
    logger.info("GET /employees/count — %d", count)
    return {"table": "employees", "count": count}


@counts_router.get("/offices/count")
def get_office_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the offices table."""
    logger.info("GET /offices/count")
    count = crud.count_offices(db)
    logger.info("GET /offices/count — %d", count)
    return {"table": "offices", "count": count}


@counts_router.get("/payments/count")
def get_payment_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the payments table."""
    logger.info("GET /payments/count")
    count = crud.count_payments(db)
    logger.info("GET /payments/count — %d", count)
    return {"table": "payments", "count": count}


@counts_router.get("/orderdetails/count")
def get_orderdetail_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the orderdetails table."""
    logger.info("GET /orderdetails/count")
    count = crud.count_orderdetails(db)
    logger.info("GET /orderdetails/count — %d", count)
    return {"table": "orderdetails", "count": count}


@counts_router.get("/productlines/count")
def get_productline_count(db: Session = Depends(get_db)):
    """Returns the total number of rows in the productlines table."""
    logger.info("GET /productlines/count")
    count = crud.count_productlines(db)
    logger.info("GET /productlines/count — %d", count)
    return {"table": "productlines", "count": count}


# ── Aggregated Dashboard with Concurrency ──────────────────────────────────────

def _count_in_own_session(count_fn):
    """Run a count function with its own DB session (thread-safe)."""
    db = SessionLocal()
    try:
        return count_fn(db)
    finally:
        db.close()


@counts_router.get("/overall_counts", tags=["Dashboard"])
async def get_overall_counts():
    """
    Fetches record counts from all 8 tables SIMULTANEOUSLY using asyncio.gather().
    Each query runs in its own thread with its own DB session for thread safety.

    Returns combined JSON:
    {
        "customers": 122,
        "orders": 326,
        "products": 110,
        "employees": 23,
        "offices": 7,
        "payments": 273,
        "orderdetails": 2996,
        "productlines": 7,
        "response_time_ms": 45.2
    }
    """
    logger.info("GET /overall_counts — starting all 8 concurrent queries")
    start_time = time.perf_counter()

    # ── Launch all 8 DB queries at the same time ───────────────────────────
    # Each task gets its OWN session via _count_in_own_session (thread-safe).
    # asyncio.to_thread() moves each blocking SQLAlchemy call off the event
    # loop into a thread, allowing true concurrent execution.
    logger.info("Launching asyncio.gather() for 8 concurrent DB queries...")

    (
        customers,
        orders,
        products,
        employees,
        offices,
        payments,
        orderdetails,
        productlines,
    ) = await asyncio.gather(
        asyncio.to_thread(_count_in_own_session, crud.count_customers),
        asyncio.to_thread(_count_in_own_session, crud.count_orders),
        asyncio.to_thread(_count_in_own_session, crud.count_products),
        asyncio.to_thread(_count_in_own_session, crud.count_employees),
        asyncio.to_thread(_count_in_own_session, crud.count_offices),
        asyncio.to_thread(_count_in_own_session, crud.count_payments),
        asyncio.to_thread(_count_in_own_session, crud.count_orderdetails),
        asyncio.to_thread(_count_in_own_session, crud.count_productlines),
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info("asyncio.gather() completed in %s ms", elapsed_ms)

    result = {
        "customers": customers,
        "orders": orders,
        "products": products,
        "employees": employees,
        "offices": offices,
        "payments": payments,
        "orderdetails": orderdetails,
        "productlines": productlines,
        "response_time_ms": elapsed_ms,
    }

    logger.info("GET /overall_counts — success: %s", result)
    return result
