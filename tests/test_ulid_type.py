import pytest
from app.models.ulid_type import ULIDType
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column
from ulid import ULID

Base = declarative_base()


class ULIDTestModel(Base):
    __tablename__ = "ulid_test"
    id: Mapped[ULID] = mapped_column(
        ULIDType(), primary_key=True, default=lambda: ULID()
    )
    name: Mapped[str] = mapped_column()


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    with Session(engine) as sess:
        yield sess


def test_ulid_type_roundtrip(session):
    # Arrange
    ulid_obj = ULID()
    test_obj = ULIDTestModel(id=ulid_obj, name="test")
    session.add(test_obj)
    session.commit()
    # Act
    result = session.execute(
        select(ULIDTestModel).where(ULIDTestModel.id == ulid_obj)
    ).scalar_one()
    # Assert
    assert isinstance(result.id, ULID)
    assert str(result.id) == str(ulid_obj)
    assert result.name == "test"


def test_ulid_type_from_str(session):
    ulid_str = str(ULID())
    test_obj = ULIDTestModel(id=ulid_str, name="strtest")
    session.add(test_obj)
    session.commit()
    result = session.execute(
        select(ULIDTestModel).where(ULIDTestModel.name == "strtest")
    ).scalar_one()
    assert isinstance(result.id, ULID)
    assert str(result.id) == ulid_str
