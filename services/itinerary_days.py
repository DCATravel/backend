import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.itinerary_days import Itinerary_days

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Itinerary_daysService:
    """Service layer for Itinerary_days operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Itinerary_days]:
        """Create a new itinerary_days"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Itinerary_days(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created itinerary_days with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating itinerary_days: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: str) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for itinerary_days {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[str] = None) -> Optional[Itinerary_days]:
        """Get itinerary_days by ID (user can only see their own records)"""
        try:
            query = select(Itinerary_days).where(Itinerary_days.id == obj_id)
            if user_id:
                query = query.where(Itinerary_days.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching itinerary_days {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[str] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of itinerary_dayss (user can only see their own records)"""
        try:
            query = select(Itinerary_days)
            count_query = select(func.count(Itinerary_days.id))
            
            if user_id:
                query = query.where(Itinerary_days.user_id == user_id)
                count_query = count_query.where(Itinerary_days.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Itinerary_days, field):
                        query = query.where(getattr(Itinerary_days, field) == value)
                        count_query = count_query.where(getattr(Itinerary_days, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Itinerary_days, field_name):
                        query = query.order_by(getattr(Itinerary_days, field_name).desc())
                else:
                    if hasattr(Itinerary_days, sort):
                        query = query.order_by(getattr(Itinerary_days, sort))
            else:
                query = query.order_by(Itinerary_days.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching itinerary_days list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Itinerary_days]:
        """Update itinerary_days (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Itinerary_days {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated itinerary_days {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating itinerary_days {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[str] = None) -> bool:
        """Delete itinerary_days (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Itinerary_days {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted itinerary_days {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting itinerary_days {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Itinerary_days]:
        """Get itinerary_days by any field"""
        try:
            if not hasattr(Itinerary_days, field_name):
                raise ValueError(f"Field {field_name} does not exist on Itinerary_days")
            result = await self.db.execute(
                select(Itinerary_days).where(getattr(Itinerary_days, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching itinerary_days by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Itinerary_days]:
        """Get list of itinerary_dayss filtered by field"""
        try:
            if not hasattr(Itinerary_days, field_name):
                raise ValueError(f"Field {field_name} does not exist on Itinerary_days")
            result = await self.db.execute(
                select(Itinerary_days)
                .where(getattr(Itinerary_days, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Itinerary_days.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching itinerary_dayss by {field_name}: {str(e)}")
            raise