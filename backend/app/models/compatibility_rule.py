from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class CompatibilityRule(SQLModel, table=True):
    __tablename__ = "compatibility_rules"

    id: str = Field(primary_key=True)
    rule_name: str
    applies_to_component_id: Optional[str] = None
    applies_to_category: Optional[str] = None
    condition_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    severity: str = "warning"
    message: str
    required_component_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    required_component_categories: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    blocking: bool = True
