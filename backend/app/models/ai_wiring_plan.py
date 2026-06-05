from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class AIWiringPlan(SQLModel, table=True):
    __tablename__ = "ai_wiring_plans"

    id: str = Field(primary_key=True)
    project_id: Optional[str] = None
    input_component_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    project_description: str = ""
    raw_ai_response_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    validated_plan_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: str = "pending"
    errors_json: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
