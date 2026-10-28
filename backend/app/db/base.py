from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared metadata; domain models will be imported by migration env explicitly."""
