from typing import List
from fastapi import APIRouter, HTTPException, status

from server.db.store import store
from server.models.schemas import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=List[Customer])
async def list_customers():
    """List all customer accounts."""
    return store.list_customers()


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Retrieve details for a specific customer."""
    customer = store.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found",
        )
    return customer

