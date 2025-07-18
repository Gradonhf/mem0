"""
Custom pagination utilities that use modern SQLAlchemy Select objects
to avoid deprecation warnings from fastapi-pagination.
"""

from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy import Select, func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.sql import select as sa_select

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def paginate_select(
    db: Session,
    select_stmt: Select,
    model: Type,
    page: int = 1,
    size: int = 10,
    transformer=None
) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy Select statement using modern SQLAlchemy 2.0 approach.
    Builds a separate count query to avoid issues with DISTINCT ON and complex joins.
    
    Args:
        db: Database session
        select_stmt: SQLAlchemy Select statement
        model: The SQLAlchemy model class (e.g., Memory)
        page: Page number (1-based)
        size: Page size
        transformer: Optional function to transform items
    
    Returns:
        PaginatedResponse with items and metadata
    """
    # Calculate offset
    offset = (page - 1) * size
    
    # Build a simple count query: SELECT COUNT(DISTINCT model.id) FROM model
    count_query = sa_select(func.count(func.distinct(model.id))).select_from(model)
    
    # Apply the same WHERE conditions from the original query
    if hasattr(select_stmt, '_where_criteria') and select_stmt._where_criteria:
        for criterion in select_stmt._where_criteria:
            # Only apply criteria that reference the main model
            if str(criterion).find(f'{model.__name__.lower()}.') != -1:
                count_query = count_query.where(criterion)
    
    # Execute count query
    total = db.execute(count_query).scalar()
    
    # Apply pagination to the original select
    paginated_stmt = select_stmt.offset(offset).limit(size)
    
    # Execute paginated query
    result = db.execute(paginated_stmt)
    items = result.scalars().unique().all()
    
    # Apply transformer if provided
    if transformer:
        items = [transformer(item) for item in items]
    
    # Calculate pages
    pages = (total + size - 1) // size if total > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

def create_select_from_query(query) -> Select:
    """
    Convert a SQLAlchemy Query object to a Select statement.
    This is a helper function to migrate from Query to Select.
    """
    # Extract the underlying select statement from the query
    return query.statement 