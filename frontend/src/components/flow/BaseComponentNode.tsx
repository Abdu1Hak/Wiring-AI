"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";

import { cn } from "@/lib/utils";
import type { ComponentNodeData } from "@/types/wiring";

const positionMap = {
  left: Position.Left,
  right: Position.Right,
  top: Position.Top,
  bottom: Position.Bottom,
};

const categoryStyles: Record<string, string> = {
  controller: "border-blue-500 bg-blue-50",
  sensor: "border-emerald-500 bg-emerald-50",
  output: "border-amber-500 bg-amber-50",
  display: "border-violet-500 bg-violet-50",
  driver: "border-orange-500 bg-orange-50",
  passive: "border-slate-500 bg-slate-50",
  support: "border-gray-400 bg-gray-50",
  power: "border-red-400 bg-red-50",
  default: "border-zinc-400 bg-white",
};

export function BaseComponentNode({ data }: NodeProps) {
  const nodeData = data as ComponentNodeData;
  const style = categoryStyles[nodeData.category] ?? categoryStyles.default;

  return (
    <div className={cn("min-w-[180px] rounded-lg border-2 px-3 py-2 shadow-sm", style)}>
      <div className="mb-2 text-sm font-semibold text-zinc-900">{nodeData.label}</div>
      <div className="space-y-1">
        {nodeData.pins.map((pin) => {
          const isTarget =
            pin.direction === "input" ||
            pin.direction === "power_input" ||
            pin.direction === "ground";
          return (
            <div key={pin.handleId} className="relative flex items-center justify-between text-xs">
              <Handle
                id={pin.handleId}
                type={isTarget ? "target" : "source"}
                position={positionMap[pin.position] ?? Position.Right}
                className="!h-2.5 !w-2.5 !border-2 !border-white !bg-zinc-800"
              />
              <span className="mx-2 flex-1 text-zinc-600">{pin.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
