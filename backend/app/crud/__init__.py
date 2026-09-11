"""Database CRUD layer."""

from app.crud.crud_monument import monument_crud
from app.crud.crud_review import review_crud

__all__ = ["monument_crud", "review_crud"]
