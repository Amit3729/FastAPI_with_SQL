import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Customer,Order, Payment,Product, ProductLine, Employee, Office, OrderDetail

import schemas

logger = logging.getLogger(__name__)

#Create
def create_customer(db: Session, customer_data: schemas.CustomerCreate)->Customer:
    """
    Insert new customer into database
    """
    logger.info(  "CREATE: Adding new customer '%s'.", customer_data.customerName)
    new_customer = Customer(**customer_data.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    logger.info("CREATE: Customer '%s' created with ID %d.",
                new_customer.customerName, new_customer.customerNumber)
    return new_customer


#READ
def get_customer(db: Session, customer_number: int)->Customer:
    """ Fetch one customer by primary key.
    Returns None (not an exception) when the ID doesn't exist —
    the router decides whether to raise 404."""

    logger.info("READ: Fetching customer #%d.", customer_number)
    customer = db.query(Customer).filter(Customer.customerNumber == customer_number).first()
    if customer is None:
        logger.warning(" READ: Customer #%d not found.", customer_number)
    else:
          logger.info("READ: Customer #%d found — '%s'.",
                    customer_number, customer.customerName)
    return customer

#Read (list with pignation)
def get_customers(db: Session, skip: int = 0, limit:int=5)->list[Customer]:
    """ Return a paginated list of customers.
    skip = offset  (e.g. skip=20 starts from the 21st record)
    limit = page size (e.g. limit=10 returns 10 at a time)"""
    logger.info(" READ: Listing customers — skip=%d, limit=%d.", skip, limit)
    customers = db.query(Customer).offset(skip).limit(limit).all()
    logger.info("READ: Returned %d customer(s).", len(customers))
    return customers

# UPDATE
def update_customer(
    db: Session,
    customer_number: int,
    update_data: schemas.CustomerUpdate
) -> Customer | None:
    """
    Apply a partial update. Only fields explicitly set in update_data are changed.
    Returns None if the customer doesn't exist.
    """
    logger.info("UPDATE: Updating customer #%d.", customer_number)
    customer = get_customer(db, customer_number)
 
    if customer is None:
        return None
 
    # exclude_unset=True means we only update what the user actually sent
    changes = update_data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(customer, field, value)
        logger.debug("   → Set '%s' = %r", field, value)
 
    db.commit()
    db.refresh(customer)
    logger.info("UPDATE: Customer #%d updated successfully.", customer_number)
    return customer
 
 
# DELETE 
 
def delete_customer(db: Session, customer_number: int) -> bool:
    """
    Delete a customer by primary key.
    Returns True on success, False if the record was not found.
    """
    logger.info("🗑️  DELETE: Deleting customer #%d.", customer_number)
    customer = get_customer(db, customer_number)
 
    if customer is None:
        logger.warning("DELETE: Customer #%d not found — nothing deleted.", customer_number)
        return False
 
    db.delete(customer)
    db.commit()
    logger.info(" DELETE: Customer #%d deleted.", customer_number)
    return True
 
#COUNT FUNCTIONS (one per table) 
def count_customers(db: Session) -> int:
    logger.info("COUNT: Querying customers table.")
    result = db.query(func.count()).select_from(Customer).scalar()
    count = result or 0
    logger.info("COUNT: customers = %d", count)
    return count
 
 
def count_orders(db: Session) -> int:
    logger.info("COUNT: Querying orders table.")
    result = db.query(func.count()).select_from(Order).scalar()
    count = result or 0
    logger.info("COUNT: orders = %d", count)
    return count
 
 
def count_products(db: Session) -> int:
    logger.info("📊 COUNT: Querying products table.")
    result = db.query(func.count()).select_from(Product).scalar()
    count = result or 0
    logger.info("COUNT: products = %d", count)
    return count
 
 
def count_employees(db: Session) -> int:
    logger.info("📊 COUNT: Querying employees table.")
    result = db.query(func.count()).select_from(Employee).scalar()
    count = result or 0
    logger.info("COUNT: employees = %d", count)
    return count
 
 
def count_offices(db: Session) -> int:
    logger.info("COUNT: Querying offices table.")
    result = db.query(func.count()).select_from(Office).scalar()
    count = result or 0
    logger.info("COUNT: offices = %d", count)
    return count
 
 
def count_payments(db: Session) -> int:
    logger.info("COUNT: Querying payments table.")
    result = db.query(func.count()).select_from(Payment).scalar()
    count = result or 0
    logger.info("COUNT: payments = %d", count)
    return count
 
 
def count_orderdetails(db: Session) -> int:
    logger.info("COUNT: Querying orderdetails table.")
    result = db.query(func.count()).select_from(OrderDetail).scalar()
    count = result or 0
    logger.info("COUNT: orderdetails = %d", count)
    return count
 
 
def count_productlines(db: Session) -> int:
    logger.info("COUNT: Querying productlines table.")
    result = db.query(func.count()).select_from(ProductLine).scalar()
    count = result or 0
    logger.info("COUNT: productlines = %d", count)
    return count
 

     