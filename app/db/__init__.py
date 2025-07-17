"""Database module for Clinical Sample Service."""

from .base import (
    AsyncSessionLocal,
    Base,
    close_db,
    create_tables,
    drop_tables,
    engine,
    get_db,
)

# Import models here when they are created
# This ensures that Alembic can discover all models
# from ..models.user import User
# from ..models.sample import Sample

__all__ = [
    "Base",
    "get_db",
    "engine",
    "AsyncSessionLocal",
    "create_tables",
    "drop_tables",
    "close_db",
]
