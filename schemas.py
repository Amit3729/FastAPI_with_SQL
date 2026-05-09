from pydantic import BaseModel, field_validator
from typing import Optional , List
from datetime import date
from decimal import Decimal
import logging
logger = logging.getLogger(__name__)
#related data
class OrderSchema(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: str
    comments: Optional[str] = None

    model_config = {"from_attributes": True}

class PaymentOut(BaseModel):
    checkNumber: str 
    paymentDate: date
    amount: Decimal
    model_config = {"from_attributes": True}

#customer schema
class CustomerCreate(BaseModel):
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str 
    adressLine1: str
    addressLine2: Optional[str]    = None
    city: str 
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber:    Optional[int]    = None
    creditLimit:               Optional[Decimal] = None
 
    @field_validator("customerName", "contactLastName", "contactFirstName", mode="before")
    @classmethod
    def must_not_be_empty(cls, value: str)->str:
        if not value or not value.strip():
            logger.warning("Validation Error: required filed are empty")
            raise ValueError("Field must not be empty")
        return value

    @field_validator("creditLimit", mode="before")
    @classmethod
    def credit_must_non_negative(cls, value):
        if value is not None and Decimal(str(value)) < 0:
            logger.warning("Validation Error: Credit Limit negative")
            raise ValueError("field must not be empty")
        return value


class CustomerOut(BaseModel):
        """
        What API return to users
        """ 
        customerNumber:            int
        customerName: str
        contactLastName: str
        contactFirstName: str
        phone: str
        addressLine1: str
        addressLine2: Optional[str] = None
        city: str
        state: Optional[str] = None
        postalCode: Optional[str] = None
        country: str
        salesRepEmployeeNumber: Optional[int] = None
        creditLimit: Optional[Decimal] = None
    
        orders: List[OrderSchema] = []
        payments: List[PaymentOut] = []
    
        model_config = {"from_attributes": True}
    

class CustomerUpdate(BaseModel):
    """
    Used for partial updates (PATCH). Every field is Optional —
    the user only needs to send what they want to change
    """
    customerName: Optional[str] = None
    contactLastName: Optional[str] = None
    contactFirstName: Optional[str] = None
    phone: Optional[str] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    salesRepEmployeeNumber: Optional[int]= None
    creditLimit: Optional[Decimal] = None
