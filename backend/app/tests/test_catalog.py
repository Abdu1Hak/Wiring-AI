from sqlmodel import Session, select

from app.models import Component, ComponentPin
from app.seed.catalog_data import build_catalog


def test_catalog_has_at_least_50_components():
    components, pins, rules = build_catalog()
    assert len(components) >= 50
    assert len(pins) > 50
    assert len(rules) >= 3


def test_seed_database(session: Session):
    count = len(session.exec(select(Component)).all())
    assert count >= 50
    pin_count = len(session.exec(select(ComponentPin)).all())
    assert pin_count > 50
