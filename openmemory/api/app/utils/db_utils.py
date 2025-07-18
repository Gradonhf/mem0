from sqlalchemy.orm import Session
from app.models import Memory


def get_database_dialect(db: Session) -> str:
    """Get the database dialect name."""
    return db.bind.dialect.name


def build_memory_query_with_distinct(db: Session, base_query, order_by_field=None):
    """
    Build a memory query with DISTINCT ON that works for both SQLite and PostgreSQL.
    This preserves the exact same functionality across databases.
    
    Args:
        db: Database session
        base_query: Base query to modify
        order_by_field: Field to order by (defaults to Memory.created_at.desc())
    
    Returns:
        Modified query with DISTINCT ON and appropriate ORDER BY
    """
    dialect = get_database_dialect(db)
    
    if order_by_field is None:
        order_by_field = Memory.created_at.desc()
    
    if dialect == 'postgresql':
        # PostgreSQL: DISTINCT ON requires ORDER BY to start with the same column
        return base_query.distinct(Memory.id).order_by(
            Memory.id,  # Must come first for DISTINCT ON
            order_by_field
        )
    else:
        # SQLite: Can use DISTINCT ON with any ORDER BY
        return base_query.distinct(Memory.id).order_by(order_by_field)


# Alias for backward compatibility
build_memory_query_simple = build_memory_query_with_distinct 