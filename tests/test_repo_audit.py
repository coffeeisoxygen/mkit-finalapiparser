import uuid

import pytest
from app.custom.exceptions.cst_exceptions import AuditMixinError
from app.database.repositories.repo_audit import AuditMixinRepository
from app.models.db_user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_audit_soft_delete_and_restore(test_db_session):
    actor_id = uuid.uuid4()
    # Create dummy user
    user = User(
        username="audituser",
        email="audituser@example.com",
        full_name="Audit User",
        hashed_password="hashed",
    )
    test_db_session.add(user)
    await test_db_session.commit()
    repo = AuditMixinRepository(test_db_session, User)
    # Soft delete
    await repo.soft_delete(str(user.id), str(actor_id))
    result = await test_db_session.execute(select(User).where(User.id == str(user.id)))
    fetched = result.scalar_one_or_none()
    assert fetched.is_deleted_flag is True
    assert str(fetched.deleted_by) == str(actor_id)
    assert fetched.deleted_at is not None
    # Restore
    await repo.restore(str(user.id))
    result2 = await test_db_session.execute(select(User).where(User.id == str(user.id)))
    restored = result2.scalar_one_or_none()
    assert restored.is_deleted_flag is False
    assert restored.deleted_by is None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_audit_get_audit_log(test_db_session):
    actor_id = uuid.uuid4()
    user = User(
        username="auditloguser",
        email="auditloguser@example.com",
        full_name="Audit Log User",
        hashed_password="hashed",
    )
    test_db_session.add(user)
    await test_db_session.commit()
    repo = AuditMixinRepository(test_db_session, User)
    await repo.soft_delete(str(user.id), str(actor_id))
    audit_log = await repo.get_audit_log(str(user.id))
    assert audit_log["deleted_by"] == str(actor_id)
    assert audit_log["deleted_at"] is not None


@pytest.mark.asyncio
async def test_audit_soft_delete_not_found(test_db_session):
    repo = AuditMixinRepository(test_db_session, User)
    invalid_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    with pytest.raises(AuditMixinError):
        await repo.soft_delete(invalid_id, actor_id)
    with pytest.raises(AuditMixinError):
        await repo.restore(invalid_id)
    audit_log = await repo.get_audit_log(invalid_id)
    assert audit_log == {}
