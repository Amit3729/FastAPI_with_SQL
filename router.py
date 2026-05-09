import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/customers", tags=["Customers"])

# GET / cutomers-paginated list
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
    logger.info(" GET /customers — skip=%d, limit=%d", skip, limit)
    customers = crud.get_customers(db, skip=skip, limit=limit)
    logger.info("GET /customers — returning %d record(s)", len(customers))
    return customers

# Get/Customer/{customerNumber} single customer with related data
@router.get("/{customer_number}", response_model=schemas.CustomerOut)
def get_customer(customer_number: int, db: Session = Depends(get_db)):
    """  Returns a single customer including their orders and payments.
 
    - Returns **404** if the customer number does not exist.
    - Orders and payments are returned as nested lists (empty list if none)."""
    logger.info("GET /customers/%d", customer_number)
    customer = crud.get_customer(db, customer_number)

    if customer is None:
        logger.warning( "GET /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")
    logger.info("GET /customers/%d — found customer '%s'", customer_number, customer.customerName)
    return customer

#POST
@router.post("/", response_model=schemas.CustomerCreate, status_code=201)
def create_customer(customer_data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """ Creates a new customer. The database auto-assigns the customerNumber.
 
    - Pydantic validates all fields before the DB is touched.
    - Returns the created customer with its new ID."""
    logger.info("POST /customers - creating customer '%s'", customer_data.customerName)
    new_customer = crud.create_customer(db, customer_data)
    logger.info("POST /customers — created customer #%d", new_customer.customerNumber)
    return new_customer

#Patch->/customers/{customerNumber}- partial update
@router.patch("/{customer_number}", response_model=schemas.CustomerOut)
def update_customer(
    customer_number: int,
    update_data: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    """ Partially updates a customer. Only send the fields you want to change.
 
    - Returns **404** if the customer number does not exist."""
    logger.info("PATCH /customers/%d - updating customer", customer_number)
    updated = crud.update_customer(db, customer_number, update_data)

    if updated is None:
        logger.warning("📤 PATCH /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")
    
    logger.info("PATCH /customers/%d — updated successfully", customer_number)
    return updated


#DELETE
@router.delete("/{customer_number}", status_code=204)
def delete_customer(customer_number: int, db:Session = Depends(get_db)):
    """ Deletes a customer by ID.
 
    - Returns **204 No Content** on success.
    - Returns **404** if the customer number does not exist."""
    logger.info("DELETE /customers/%d - deletinng customer", customer_number)
    deleted = crud.delete_customer(db, customer_number)

    if not deleted:
        logger.warning("DELETE /customers/%d — 404 Not Found", customer_number)
        raise HTTPException(status_code=404, detail=f"Customer #{customer_number} not found")
    logger.info("DELETE /customers/%d — deleted successfully", customer_number)

        
    

