from typing import Optional

from sqlmodel import Field, SQLModel


class ComponentPin(SQLModel, table=True):
    __tablename__ = "component_pins"

    id: str = Field(primary_key=True)
    component_id: str = Field(foreign_key="components.id", index=True)
    pin_id: str
    name: str
    label: str
    pin_type: str
    direction: str
    position: str = "right"
    allowed_voltage_min: Optional[float] = None
    allowed_voltage_max: Optional[float] = None
    logic_voltage: Optional[float] = None
    protocol: Optional[str] = None
    can_source_current: bool = False
    can_sink_current: bool = False
    max_current_ma: Optional[float] = None
    react_flow_handle_id: str
    notes: Optional[str] = None
