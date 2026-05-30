import {
  Background,
  Controls,
  ReactFlow,
  MarkerType,
} from "@xyflow/react";
import ComponentNode from "./ComponentNode";

const nodeTypes = {
  componentNode: ComponentNode,
};

function getWireColor(label = "") {
  const key = label.toLowerCase();

  if (key.includes("power")) return "#ef4444";
  if (key.includes("ground")) return "#111827";
  if (key.includes("trigger")) return "#2563eb";
  if (key.includes("echo")) return "#7c3aed";
  if (key.includes("signal")) return "#f97316";
  if (key.includes("current")) return "#ca8a04";

  return "#334155";
}

export default function WiringCanvas({ nodes, edges }) {
  const styledEdges = edges.map((edge) => {
    const color = getWireColor(edge.label);

    return {
      ...edge,
      type: "smoothstep",
      animated: false,
      interactionWidth: 24,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color,
      },
      style: {
        strokeWidth: 4,
        stroke: color,
      },
      labelStyle: {
        fontSize: 12,
        fontWeight: 700,
        fill: color,
      },
      labelBgStyle: {
        fill: "white",
        fillOpacity: 0.9,
      },
      labelBgPadding: [6, 4],
      labelBgBorderRadius: 6,
    };
  });

  return (
    <div className="h-[760px] w-full rounded-xl border bg-white">
      <ReactFlow
        nodes={nodes}
        edges={styledEdges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
      >
        <Background gap={18} size={1} />
        <Controls />
      </ReactFlow>
    </div>
  );
}