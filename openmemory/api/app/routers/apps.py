from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models import App, Memory, MemoryAccessLog, MemoryState, User
from app.config import USER_ID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/api/v1/apps", tags=["apps"])

# Pydantic models
class CreateAppRequest(BaseModel):
    name: str
    description: Optional[str] = None
    metadata: dict = {}

# Helper functions
def get_app_or_404(db: Session, app_id: UUID) -> App:
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app

def get_user_or_404(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# List all apps with filtering
@router.get("/")
async def list_apps(
    user_id: str,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = 'name',
    sort_direction: str = 'asc',
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Get the user
    user = get_user_or_404(db, user_id)
    
    # Create a subquery for memory counts (only for this user)
    memory_counts = db.query(
        Memory.app_id,
        func.count(Memory.id).label('memory_count')
    ).filter(
        Memory.state.in_([MemoryState.active, MemoryState.paused, MemoryState.archived]),
        Memory.user_id == user.id
    ).group_by(Memory.app_id).subquery()

    # Create a subquery for access counts (only for this user's memories)
    access_counts = db.query(
        MemoryAccessLog.app_id,
        func.count(func.distinct(MemoryAccessLog.memory_id)).label('access_count')
    ).join(
        Memory,
        MemoryAccessLog.memory_id == Memory.id
    ).filter(
        Memory.user_id == user.id
    ).group_by(MemoryAccessLog.app_id).subquery()

    # Base query - filter apps by owner
    query = db.query(
        App,
        func.coalesce(memory_counts.c.memory_count, 0).label('total_memories_created'),
        func.coalesce(access_counts.c.access_count, 0).label('total_memories_accessed')
    ).filter(
        App.owner_id == user.id
    )

    # Join with subqueries
    query = query.outerjoin(
        memory_counts,
        App.id == memory_counts.c.app_id
    ).outerjoin(
        access_counts,
        App.id == access_counts.c.app_id
    )

    if name:
        query = query.filter(App.name.ilike(f"%{name}%"))

    if is_active is not None:
        query = query.filter(App.is_active == is_active)

    # Apply sorting
    if sort_by == 'name':
        sort_field = App.name
    elif sort_by == 'memories':
        sort_field = func.coalesce(memory_counts.c.memory_count, 0)
    elif sort_by == 'memories_accessed':
        sort_field = func.coalesce(access_counts.c.access_count, 0)
    else:
        sort_field = App.name  # default sort

    if sort_direction == 'desc':
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)

    total = query.count()
    apps = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "apps": [
            {
                "id": app[0].id,
                "name": app[0].name,
                "is_active": app[0].is_active,
                "total_memories_created": app[1],
                "total_memories_accessed": app[2]
            }
            for app in apps
        ]
    }

# Get app details
@router.get("/{app_id}")
async def get_app_details(
    app_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    # Get the user
    user = get_user_or_404(db, user_id)
    
    app = get_app_or_404(db, app_id)
    
    # Verify that the app belongs to the user
    if app.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this app")

    # Get memory access statistics (only for this user's memories)
    access_stats = db.query(
        func.count(MemoryAccessLog.id).label("total_memories_accessed"),
        func.min(MemoryAccessLog.accessed_at).label("first_accessed"),
        func.max(MemoryAccessLog.accessed_at).label("last_accessed")
    ).join(
        Memory,
        MemoryAccessLog.memory_id == Memory.id
    ).filter(
        MemoryAccessLog.app_id == app_id,
        Memory.user_id == user.id
    ).first()

    return {
        "is_active": app.is_active,
        "total_memories_created": db.query(Memory)
            .filter(Memory.app_id == app_id, Memory.user_id == user.id)
            .count(),
        "total_memories_accessed": access_stats.total_memories_accessed or 0,
        "first_accessed": access_stats.first_accessed,
        "last_accessed": access_stats.last_accessed
    }

# List memories created by app
@router.get("/{app_id}/memories")
async def list_app_memories(
    app_id: UUID,
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Get the user
    user = get_user_or_404(db, user_id)
    
    app = get_app_or_404(db, app_id)
    
    # Verify that the app belongs to the user
    if app.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this app")
    
    query = db.query(Memory).filter(
        Memory.app_id == app_id,
        Memory.user_id == user.id,
        Memory.state.in_([MemoryState.active, MemoryState.paused, MemoryState.archived])
    )
    # Add eager loading for categories
    query = query.options(joinedload(Memory.categories))
    total = query.count()
    memories = query.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "memories": [
            {
                "id": memory.id,
                "content": memory.content,
                "created_at": memory.created_at,
                "state": memory.state.value,
                "app_id": memory.app_id,
                "categories": [category.name for category in memory.categories],
                "metadata_": memory.metadata_
            }
            for memory in memories
        ]
    }

# List memories accessed by app
@router.get("/{app_id}/accessed")
async def list_app_accessed_memories(
    app_id: UUID,
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Get the user
    user = get_user_or_404(db, user_id)
    
    app = get_app_or_404(db, app_id)
    
    # Verify that the app belongs to the user
    if app.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this app")
    
    # Get memories with access counts (only for this user's memories)
    query = db.query(
        Memory,
        func.count(MemoryAccessLog.id).label("access_count")
    ).join(
        MemoryAccessLog,
        Memory.id == MemoryAccessLog.memory_id
    ).filter(
        MemoryAccessLog.app_id == app_id,
        Memory.user_id == user.id
    ).group_by(
        Memory.id
    ).order_by(
        desc("access_count")
    )

    # Add eager loading for categories
    query = query.options(joinedload(Memory.categories))

    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "memories": [
            {
                "memory": {
                    "id": memory.id,
                    "content": memory.content,
                    "created_at": memory.created_at,
                    "state": memory.state.value,
                    "app_id": memory.app_id,
                    "app_name": memory.app.name if memory.app else None,
                    "categories": [category.name for category in memory.categories],
                    "metadata_": memory.metadata_
                },
                "access_count": count
            }
            for memory, count in results
        ]
    }


@router.put("/{app_id}")
async def update_app_details(
    app_id: UUID,
    is_active: bool,
    db: Session = Depends(get_db)
):
    app = get_app_or_404(db, app_id)
    app.is_active = is_active
    db.commit()
    return {"status": "success", "message": "Updated app details successfully"}

# Create new app
@router.post("/")
async def create_app(
    request: CreateAppRequest,
    user_id: str = USER_ID,
    db: Session = Depends(get_db)
):
    # Get the user
    user = get_user_or_404(db, user_id)
    
    # Validate app name format
    import re
    if not re.match(r'^[a-z0-9-]+$', request.name):
        raise HTTPException(
            status_code=400,
            detail="App name must contain only lowercase letters, numbers, and hyphens"
        )
    
    # Check if app with this name already exists for this user
    existing_app = db.query(App).filter(
        App.name == request.name,
        App.owner_id == user.id
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=400, 
            detail=f"App with name '{request.name}' already exists for this user"
        )
    
    # Create new app
    app = App(
        owner_id=user.id,
        name=request.name,
        description=request.description,
        metadata_=request.metadata,
        is_active=True
    )
    
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {
        "id": app.id,
        "name": app.name,
        "description": app.description,
        "is_active": app.is_active,
        "total_memories_created": 0,
        "total_memories_accessed": 0
    }
