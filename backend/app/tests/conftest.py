import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import CompatibilityRule, Component, ComponentPin
from app.seed.catalog_data import build_catalog


def _seed_session(session: Session) -> None:
    if session.exec(select(Component)).first():
        return
    components, pins, rules = build_catalog()
    for component_data in components:
        session.add(Component(**component_data))
    for pin_data in pins:
        session.add(ComponentPin(**pin_data))
    for rule_data in rules:
        session.add(CompatibilityRule(**rule_data))
    session.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_session(session)
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
