from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(
        self, 
        db: AsyncSession, 
        id: Any,
        options: Optional[List] = None
    ) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)
        
        if options:
            query = query.options(*options)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[List] = None,
        order_by: Optional[Any] = None,
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        if options:
            query = query.options(*options)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: CreateSchemaType,
        commit: bool = True
    ) -> ModelType:
        """Create a new record."""
        obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_data)
        
        db.add(db_obj)
        
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True
    ) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        id: Any,
        commit: bool = True
    ) -> Optional[ModelType]:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            if commit:
                await db.commit()
        return obj
    
    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filtering."""
        query = select(func.count(self.model.id))
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if record exists with given filters."""
        query = select(self.model.id)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None