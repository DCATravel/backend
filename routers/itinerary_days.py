import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.itinerary_days import Itinerary_daysService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/itinerary_days", tags=["itinerary_days"])


# ---------- Pydantic Schemas ----------
class Itinerary_daysData(BaseModel):
    """Entity data schema (for create/update)"""
    itinerary_id: int
    day_number: int
    title: str
    description: str = None
    location: str = None
    notes: str = None


class Itinerary_daysUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    itinerary_id: Optional[int] = None
    day_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class Itinerary_daysResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: str
    itinerary_id: int
    day_number: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Itinerary_daysListResponse(BaseModel):
    """List response schema"""
    items: List[Itinerary_daysResponse]
    total: int
    skip: int
    limit: int


class Itinerary_daysBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Itinerary_daysData]


class Itinerary_daysBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Itinerary_daysUpdateData


class Itinerary_daysBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Itinerary_daysBatchUpdateItem]


class Itinerary_daysBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Itinerary_daysListResponse)
async def query_itinerary_dayss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query itinerary_dayss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying itinerary_dayss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Itinerary_daysService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = await service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
            user_id=str(current_user.id),
        )
        logger.debug(f"Found {result['total']} itinerary_dayss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying itinerary_dayss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Itinerary_daysListResponse)
async def query_itinerary_dayss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query itinerary_dayss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying itinerary_dayss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Itinerary_daysService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = await service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} itinerary_dayss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying itinerary_dayss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Itinerary_daysResponse)
async def get_itinerary_days(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single itinerary_days by ID (user can only see their own records)"""
    logger.debug(f"Fetching itinerary_days with id: {id}, fields={fields}")
    
    service = Itinerary_daysService(db)
    try:
        result = await service.get_by_id(id, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Itinerary_days with id {id} not found")
            raise HTTPException(status_code=404, detail="Itinerary_days not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching itinerary_days {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Itinerary_daysResponse, status_code=201)
async def create_itinerary_days(
    data: Itinerary_daysData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new itinerary_days"""
    logger.debug(f"Creating new itinerary_days with data: {data}")
    
    service = Itinerary_daysService(db)
    try:
        result = await service.create(data.model_dump(), user_id=str(current_user.id))
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create itinerary_days")
        
        logger.info(f"Itinerary_days created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating itinerary_days: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating itinerary_days: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Itinerary_daysResponse], status_code=201)
async def create_itinerary_dayss_batch(
    request: Itinerary_daysBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple itinerary_dayss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} itinerary_dayss")
    
    service = Itinerary_daysService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} itinerary_dayss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Itinerary_daysResponse])
async def update_itinerary_dayss_batch(
    request: Itinerary_daysBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple itinerary_dayss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} itinerary_dayss")
    
    service = Itinerary_daysService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=str(current_user.id))
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} itinerary_dayss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Itinerary_daysResponse)
async def update_itinerary_days(
    id: int,
    data: Itinerary_daysUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing itinerary_days (requires ownership)"""
    logger.debug(f"Updating itinerary_days {id} with data: {data}")

    service = Itinerary_daysService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=str(current_user.id))
        if not result:
            logger.warning(f"Itinerary_days with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Itinerary_days not found")
        
        logger.info(f"Itinerary_days {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating itinerary_days {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating itinerary_days {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_itinerary_dayss_batch(
    request: Itinerary_daysBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple itinerary_dayss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} itinerary_dayss")
    
    service = Itinerary_daysService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=str(current_user.id))
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} itinerary_dayss successfully")
        return {"message": f"Successfully deleted {deleted_count} itinerary_dayss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_itinerary_days(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single itinerary_days by ID (requires ownership)"""
    logger.debug(f"Deleting itinerary_days with id: {id}")
    
    service = Itinerary_daysService(db)
    try:
        success = await service.delete(id, user_id=str(current_user.id))
        if not success:
            logger.warning(f"Itinerary_days with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Itinerary_days not found")
        
        logger.info(f"Itinerary_days {id} deleted successfully")
        return {"message": "Itinerary_days deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting itinerary_days {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")