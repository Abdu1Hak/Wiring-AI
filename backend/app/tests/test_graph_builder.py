from sqlmodel import Session

from app.schemas.ai_planner_schema import AIConnection
from app.services.graph_builder_service import build_graph, node_id_for_component

def test_graph_builder_creates_handles(session: Session):
    connections = [
        AIConnection(
            id="conn_1",
            fromComponentId="arduino_uno",
            fromPinId="d9",
            toComponentId="hc_sr04",
            toPinId="trig",
            connectionType="digital_signal",
            wireColor="blue",
            purpose="Trigger",
        )
    ]
    graph = build_graph(session, ["arduino_uno", "hc_sr04"], connections)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    edge = graph.edges[0]
    assert edge.source == node_id_for_component("arduino_uno")
    assert edge.sourceHandle == "arduino_uno_d9"
    assert edge.targetHandle == "hc_sr04_trig"
