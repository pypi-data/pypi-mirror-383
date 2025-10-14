"""
base.py - SQLAlchemy declarative base.

This module provides a single declarative base class for all SQLAlchemy models.
All ORM models should inherit from this Base class.
"""

from sqlalchemy.orm import declarative_base

# -------------------------------------------------------------------
# SQLAlchemy Base model
# -------------------------------------------------------------------
Base = declarative_base()
