"""fungsi fungsi helper generic shared among queries."""

from typing import Any


def valid_record_filter(model: Any):
    """Validates the record query for the given model.

    This function constructs a query condition to filter valid records
    based on their active status, deletion status, and deletion timestamp.

    Args:
        model (_type_): model yang akan divalidasi

    Returns:
        _type_: kondisi query untuk validasi record
    """
    return (
        (model.is_active.is_(True))
        & (model.is_deleted_flag.is_(False))
        & (model.deleted_at.is_(None))
    )


def is_valid_record(model: Any):
    return model.is_active and not model.is_deleted_flag and not model.deleted_at
