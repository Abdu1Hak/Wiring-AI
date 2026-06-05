from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import CompatibilityRule, Component, ComponentPin
from app.seed.catalog_data import build_catalog


def seed_database(force: bool = False) -> None:
    create_db_and_tables()
    components, pins, rules = build_catalog()

    with Session(engine) as session:
        existing = session.exec(select(Component)).first()
        if existing and not force:
            return

        if force:
            for model in (ComponentPin, CompatibilityRule, Component):
                for row in session.exec(select(model)).all():
                    session.delete(row)
            session.commit()

        for component_data in components:
            session.add(Component(**component_data))
        for pin_data in pins:
            session.add(ComponentPin(**pin_data))
        for rule_data in rules:
            session.add(CompatibilityRule(**rule_data))
        session.commit()


if __name__ == "__main__":
    seed_database(force=True)
    print("Database seeded.")
