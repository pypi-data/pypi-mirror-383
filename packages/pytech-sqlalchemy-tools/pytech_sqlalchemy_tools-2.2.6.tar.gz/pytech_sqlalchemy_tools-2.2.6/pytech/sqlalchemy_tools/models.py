from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

__all__ = [
    "BaseSqlModel",
]


class BaseSqlModel(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""

    pass
