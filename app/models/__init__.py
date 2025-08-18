# ruff: noqa

# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false, reportMissingImports=false

# pyright: reportUnusedImport=false
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from .member import Member # noqa: F401
