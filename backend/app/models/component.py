from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Component(SQLModel, table=True):
    __tablename__ = "components"

    id: str = Field(primary_key=True)
    name: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    description: str = ""
    frontend_node_type: str = "genericComponentNode"
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    logic_voltage: Optional[float] = None
    current_draw_ma: Optional[float] = None
    max_safe_current_ma: Optional[float] = None
    communication_protocols: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    requires_power: bool = True
    provides_power: bool = False
    is_passive: bool = False
    safety_level: str = "safe_beginner"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
