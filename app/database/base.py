"""
SQLAlchemy declarative base.
All ORM models (in models.py) inherit from this Base.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
