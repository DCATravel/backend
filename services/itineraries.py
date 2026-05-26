import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.itineraries import Itineraries

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class ItinerariesService:
    """Service layer for Itineraries operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Optional[Itineraries]:
        """Create a new itineraries"""
        try:
            obj = Itineraries(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created itineraries with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating itineraries: {str(e)}")
            raise

    async def get_by_id(self, obj_id: int) -> Optional[Itineraries]:
        """Get itineraries by ID"""
        try:
            query = select(Itineraries).where(Itineraries.id == obj_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching itineraries {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of itinerariess"""
        try:
            query = select(Itineraries)
            count_query = select(func.count(Itineraries.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Itineraries, field):
                        query = query.where(getattr(Itineraries, field) == value)
                        count_query = count_query.where(getattr(Itineraries, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Itineraries, field_name):
                        query = query.order_by(getattr(Itineraries, field_name).desc())
                else:
                    if hasattr(Itineraries, sort):
                        query = query.order_by(getattr(Itineraries, sort))
            else:
                query = query.order_by(Itineraries.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching itineraries list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Itineraries]:
        """Update itineraries"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Itineraries {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated itineraries {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating itineraries {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int) -> bool:
        """Delete itineraries"""
        try:
            obj = await self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Itineraries {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted itineraries {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting itineraries {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Itineraries]:
        """Get itineraries by any field"""
        try:
            if not hasattr(Itineraries, field_name):
                raise ValueError(f"Field {field_name} does not exist on Itineraries")
            result = await self.db.execute(
                select(Itineraries).where(getattr(Itineraries, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching itineraries by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Itineraries]:
        """Get list of itinerariess filtered by field"""
        try:
            if not hasattr(Itineraries, field_name):
                raise ValueError(f"Field {field_name} does not exist on Itineraries")
            result = await self.db.execute(
                select(Itineraries)
                .where(getattr(Itineraries, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Itineraries.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching itinerariess by {field_name}: {str(e)}")
            raise