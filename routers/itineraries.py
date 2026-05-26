import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.itineraries import ItinerariesService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/itineraries", tags=["itineraries"])


# ---------- Pydantic Schemas ----------
class ItinerariesData(BaseModel):
    """Entity data schema (for create/update)"""
    destination_id: int = None
    title: str
    description: str = None
    image_url: str = None
    duration_days: int
    duration_nights: int = None
    cities_count: int = None
    season: str = None
    price_per_person: float = None
    flight_departure_city: str = None
    flight_departure_date: str = None
    flight_arrival_city: str = None
    flight_arrival_date: str = None
    flight_return_date: str = None
    flight_stopovers: str = None
    activities: str = None
    included: str = None
    not_included: str = None
    is_active: bool = None


class ItinerariesUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    destination_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    duration_days: Optional[int] = None
    duration_nights: Optional[int] = None
    cities_count: Optional[int] = None
    season: Optional[str] = None
    price_per_person: Optional[float] = None
    flight_departure_city: Optional[str] = None
    flight_departure_date: Optional[str] = None
    flight_arrival_city: Optional[str] = None
    flight_arrival_date: Optional[str] = None
    flight_return_date: Optional[str] = None
    flight_stopovers: Optional[str] = None
    activities: Optional[str] = None
    included: Optional[str] = None
    not_included: Optional[str] = None
    is_active: Optional[bool] = None


class ItinerariesResponse(BaseModel):
    """Entity response schema"""
    id: int
    destination_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    duration_days: int
    duration_nights: Optional[int] = None
    cities_count: Optional[int] = None
    season: Optional[str] = None
    price_per_person: Optional[float] = None
    flight_departure_city: Optional[str] = None
    flight_departure_date: Optional[str] = None
    flight_arrival_city: Optional[str] = None
    flight_arrival_date: Optional[str] = None
    flight_return_date: Optional[str] = None
    flight_stopovers: Optional[str] = None
    activities: Optional[str] = None
    included: Optional[str] = None
    not_included: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItinerariesListResponse(BaseModel):
    """List response schema"""
    items: List[ItinerariesResponse]
    total: int
    skip: int
    limit: int


class ItinerariesBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[ItinerariesData]


class ItinerariesBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: ItinerariesUpdateData


class ItinerariesBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[ItinerariesBatchUpdateItem]


class ItinerariesBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=ItinerariesListResponse)
async def query_itinerariess(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query itinerariess with filtering, sorting, and pagination"""
    logger.debug(f"Querying itinerariess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = ItinerariesService(db)
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
        )
        logger.debug(f"Found {result['total']} itinerariess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying itinerariess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=ItinerariesListResponse)
async def query_itinerariess_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query itinerariess with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying itinerariess: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = ItinerariesService(db)
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
        logger.debug(f"Found {result['total']} itinerariess")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying itinerariess: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=ItinerariesResponse)
async def get_itineraries(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single itineraries by ID"""
    logger.debug(f"Fetching itineraries with id: {id}, fields={fields}")
    
    service = ItinerariesService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Itineraries with id {id} not found")
            raise HTTPException(status_code=404, detail="Itineraries not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching itineraries {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=ItinerariesResponse, status_code=201)
async def create_itineraries(
    data: ItinerariesData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new itineraries"""
    logger.debug(f"Creating new itineraries with data: {data}")
    
    service = ItinerariesService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create itineraries")
        
        logger.info(f"Itineraries created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating itineraries: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating itineraries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[ItinerariesResponse], status_code=201)
async def create_itinerariess_batch(
    request: ItinerariesBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple itinerariess in a single request"""
    logger.debug(f"Batch creating {len(request.items)} itinerariess")
    
    service = ItinerariesService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} itinerariess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[ItinerariesResponse])
async def update_itinerariess_batch(
    request: ItinerariesBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple itinerariess in a single request"""
    logger.debug(f"Batch updating {len(request.items)} itinerariess")
    
    service = ItinerariesService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} itinerariess successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=ItinerariesResponse)
async def update_itineraries(
    id: int,
    data: ItinerariesUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing itineraries"""
    logger.debug(f"Updating itineraries {id} with data: {data}")

    service = ItinerariesService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Itineraries with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Itineraries not found")
        
        logger.info(f"Itineraries {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating itineraries {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating itineraries {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_itinerariess_batch(
    request: ItinerariesBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple itinerariess by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} itinerariess")
    
    service = ItinerariesService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} itinerariess successfully")
        return {"message": f"Successfully deleted {deleted_count} itinerariess", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_itineraries(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single itineraries by ID"""
    logger.debug(f"Deleting itineraries with id: {id}")
    
    service = ItinerariesService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Itineraries with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Itineraries not found")
        
        logger.info(f"Itineraries {id} deleted successfully")
        return {"message": "Itineraries deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting itineraries {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")