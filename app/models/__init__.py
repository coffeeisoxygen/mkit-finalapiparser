# ruff: noqa

# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false, reportMissingImports=false

# pyright: reportUnusedImport=false
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.db_member import Member  # noqa: F401
from app.models.db_user import User  # noqa: F401

__all__ = ["Member", "User"]
