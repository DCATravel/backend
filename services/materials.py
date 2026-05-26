import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.materials import Materials

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class MaterialsService:
    """Service layer for Materials operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Materials]:
        """Create a new materials"""
        try:
            obj = Materials(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created materials with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating materials: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Materials]:
        """Get materials by ID"""
        try:
            query = select(Materials).where(Materials.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching materials {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of materialss"""
        try:
            query = select(Materials)
            count_query = select(func.count(Materials.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Materials, field):
                        query = query.where(getattr(Materials, field) == value)
                        count_query = count_query.where(getattr(Materials, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Materials, field_name):
                        query = query.order_by(getattr(Materials, field_name).desc())
                else:
                    if hasattr(Materials, sort):
                        query = query.order_by(getattr(Materials, sort))
            else:
                query = query.order_by(Materials.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching materials list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Materials]:
        """Update materials"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Materials {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated materials {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating materials {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete materials"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Materials {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted materials {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting materials {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Materials]:
        """Get materials by any field"""
        try:
            if not hasattr(Materials, field_name):
                raise ValueError(f"Field {field_name} does not exist on Materials")
            result = await self.db.execute(
                select(Materials).where(getattr(Materials, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching materials by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Materials]:
        """Get list of materialss filtered by field"""
        try:
            if not hasattr(Materials, field_name):
                raise ValueError(f"Field {field_name} does not exist on Materials")
            result = await self.db.execute(
                select(Materials)
                .where(getattr(Materials, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Materials.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching materialss by {field_name}: {str(e)}")
            raise