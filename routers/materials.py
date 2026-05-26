import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.materials import MaterialsService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/materials", tags=["materials"])


# ---------- Pydantic Schemas ----------
class MaterialsData(BaseModel):
    """Entity data schema (for create/update)"""
    title: str
    type: str
    destination_name: str = None
    file_url: str = None
    thumbnail_url: str = None
    dimensions: str = None


class MaterialsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    title: Optional[str] = None
    type: Optional[str] = None
    destination_name: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    dimensions: Optional[str] = None


class MaterialsResponse(BaseModel):
    """Entity response schema"""
    id: int
    title: str
    type: str
    destination_name: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    dimensions: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaterialsListResponse(BaseModel):
    """List response schema"""
    items: List[MaterialsResponse]
    total: int
    skip: int
    limit: int


class MaterialsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[MaterialsData]


class MaterialsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: MaterialsUpdateData


class MaterialsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[MaterialsBatchUpdateItem]


class MaterialsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=MaterialsListResponse)
async def query_materialss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Query materialss with filtering, sorting, and pagination"""
    logger.debug(f"Querying materialss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = MaterialsService(db)
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
        logger.debug(f"Found {result['total']} materialss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying materialss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=MaterialsListResponse)
async def query_materialss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query materialss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying materialss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = MaterialsService(db)
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
        logger.debug(f"Found {result['total']} materialss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying materialss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=MaterialsResponse)
async def get_materials(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get a single materials by ID"""
    logger.debug(f"Fetching materials with id: {id}, fields={fields}")
    
    service = MaterialsService(db)
    try:
        result = await service.get_by_id(id)
        if not result:
            logger.warning(f"Materials with id {id} not found")
            raise HTTPException(status_code=404, detail="Materials not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching materials {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=MaterialsResponse, status_code=201)
async def create_materials(
    data: MaterialsData,
    db: AsyncSession = Depends(get_db),
):
    """Create a new materials"""
    logger.debug(f"Creating new materials with data: {data}")
    
    service = MaterialsService(db)
    try:
        result = await service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create materials")
        
        logger.info(f"Materials created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating materials: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating materials: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[MaterialsResponse], status_code=201)
async def create_materialss_batch(
    request: MaterialsBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create multiple materialss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} materialss")
    
    service = MaterialsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} materialss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[MaterialsResponse])
async def update_materialss_batch(
    request: MaterialsBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update multiple materialss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} materialss")
    
    service = MaterialsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} materialss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=MaterialsResponse)
async def update_materials(
    id: int,
    data: MaterialsUpdateData,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing materials"""
    logger.debug(f"Updating materials {id} with data: {data}")

    service = MaterialsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict)
        if not result:
            logger.warning(f"Materials with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Materials not found")
        
        logger.info(f"Materials {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating materials {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating materials {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_materialss_batch(
    request: MaterialsBatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple materialss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} materialss")
    
    service = MaterialsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} materialss successfully")
        return {"message": f"Successfully deleted {deleted_count} materialss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_materials(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single materials by ID"""
    logger.debug(f"Deleting materials with id: {id}")
    
    service = MaterialsService(db)
    try:
        success = await service.delete(id)
        if not success:
            logger.warning(f"Materials with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Materials not found")
        
        logger.info(f"Materials {id} deleted successfully")
        return {"message": "Materials deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting materials {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")