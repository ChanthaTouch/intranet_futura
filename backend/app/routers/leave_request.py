from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import LeaveRequest as LeaveRequestModel, User as UserModel
from app.schemas import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse

# --- API Router Setup ---
router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"]
)

# --- POST Endpoint to Create a New Leave Request ---
@router.post(
    "/",
    response_model=LeaveRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new leave request"
)
async def create_leave_request_for_user(
    request_data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if the user exists
    result = await db.execute(select(UserModel).where(UserModel.id == request_data.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {request_data.user_id} not found."
        )

    # Create the SQLAlchemy model instance
    db_request = LeaveRequestModel(
        user_id=request_data.user_id,
        start_date=request_data.start_date,
        end_date=request_data.end_date,
        leave_type=request_data.leave_type,
        reason=request_data.reason,
        status=request_data.status,
        approver_id=request_data.approver_id,
        days=request_data.days
    )

    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    return db_request


# --- GET Endpoint to Retrieve a Specific Leave Request ---
@router.get(
    "/{request_id}",
    response_model=LeaveRequestResponse,
    summary="Retrieve a leave request by ID"
)
async def get_leave_request(
    request_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LeaveRequestModel).where(LeaveRequestModel.id == request_id))
    db_request = result.scalar_one_or_none()

    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found."
        )

    return db_request


# --- GET Endpoint to Retrieve All Leave Requests ---
@router.get(
    "/",
    response_model=List[LeaveRequestResponse],
    summary="Retrieve all leave requests"
)
async def get_all_leave_requests(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LeaveRequestModel))
    leave_requests = result.scalars().all()
    return leave_requests


# --- PUT Endpoint to Update a Leave Request ---
@router.put(
    "/{request_id}",
    response_model=LeaveRequestResponse,
    summary="Update an existing leave request by ID"
)
async def update_leave_request(
    request_id: int,
    request_data: LeaveRequestUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LeaveRequestModel).where(LeaveRequestModel.id == request_id))
    db_request = result.scalar_one_or_none()

    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found."
        )

    # Update the fields dynamically
    for field, value in request_data.model_dump(exclude_unset=True).items():
        setattr(db_request, field, value)

    await db.commit()
    await db.refresh(db_request)

    return db_request


# --- DELETE Endpoint to Delete a Leave Request ---
@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a leave request by ID"
)
async def delete_leave_request(
    request_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LeaveRequestModel).where(LeaveRequestModel.id == request_id))
    db_request = result.scalar_one_or_none()

    if db_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found."
        )

    await db.delete(db_request)
    await db.commit()

    return {"message": "Leave request deleted successfully."}
