import { Handle, Position } from "@xyflow/react";

const PIN_LAYOUTS = {
  arduino_uno: {
    left: [
      "ioref",
      "reset",
      "3v3",
      "5v",
      "gnd_1",
      "gnd_2",
      "vin",
      "a0",
      "a1",
      "a2",
      "a3",
      "a4",
      "a5",
    ],
    right: [
      "d0",
      "d1",
      "d2",
      "d3",
      "d4",
      "d5",
      "d6",
      "d7",
      "d8",
      "d9",
      "d10",
      "d11",
      "d12",
      "d13",
      "gnd_3",
      "aref",
      "sda",
      "scl",
    ],
  },

  hc_sr04: {
    left: ["vcc", "trig", "echo", "gnd"],
    right: [],
  },

  led: {
    left: ["anode"],
    right: ["cathode"],
  },

  resistor: {
    left: ["pin1"],
    right: ["pin2"],
  },
};

function getBoardStyle(componentId) {
  if (componentId === "arduino_uno") {
    return "bg-emerald-900 text-white";
  }

  if (componentId === "hc_sr04") {
    return "bg-sky-100 text-black";
  }

  if (componentId === "led") {
    return "bg-red-100 text-black";
  }

  if (componentId === "resistor") {
    return "bg-amber-100 text-black";
  }

  return "bg-white text-black";
}

function splitPins(data) {
  const layout = PIN_LAYOUTS[data.componentId];

  if (!layout) {
    const midpoint = Math.ceil(data.pins.length / 2);
    return {
      left: data.pins.slice(0, midpoint),
      right: data.pins.slice(midpoint),
    };
  }

  return {
    left: layout.left
      .map((id) => data.pins.find((pin) => pin.id === id))
      .filter(Boolean),
    right: layout.right
      .map((id) => data.pins.find((pin) => pin.id === id))
      .filter(Boolean),
  };
}

function PinRow({ pin, side, compact }) {
  const position = side === "left" ? Position.Left : Position.Right;

  return (
    <div className="relative flex items-center">
      <Handle
        type="source"
        position={position}
        id={pin.id}
        className="h-2.5 w-2.5 border border-black bg-white"
        style={side === "left" ? { left: -9 } : { right: -9 }}
      />

      <Handle
        type="target"
        position={position}
        id={pin.id}
        className="h-2.5 w-2.5 border border-black bg-white"
        style={side === "left" ? { left: -9 } : { right: -9 }}
      />

      <div
        className={`w-full rounded border border-black bg-white px-1.5 text-black ${
          compact ? "h-[17px] text-[9px] leading-[15px]" : "h-6 text-[11px] leading-5"
        }`}
      >
        {pin.label}
      </div>
    </div>
  );
}

export default function ComponentNode({ data }) {
  const componentId = data.componentId;
  const { left, right } = splitPins(data);

  const isArduino = componentId === "arduino_uno";
  const compact = isArduino;

  const boardWidth = isArduino ? 440 : 270;
  const boardHeight = isArduino
    ? 460
    : Math.max(170, 110 + Math.max(left.length, right.length) * 30);

  return (
    <div
      className={`relative rounded-2xl border-2 border-black shadow-md ${getBoardStyle(
        componentId
      )}`}
      style={{
        width: boardWidth,
        height: boardHeight,
      }}
    >
      <div
        className={`absolute left-1/2 top-1/2 z-10 flex -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-xl border-2 border-black text-center shadow-sm ${
          isArduino ? "h-24 w-36 bg-emerald-700 text-white" : "h-20 w-32 bg-white text-black"
        }`}
      >
        <div className={isArduino ? "text-base font-bold" : "text-sm font-bold"}>
          {data.label}
        </div>
        <div className="mt-1 text-[10px] opacity-75">{data.category}</div>
      </div>

      <div
        className={`absolute left-4 top-5 ${
          isArduino ? "w-[96px] space-y-1" : "w-[86px] space-y-2"
        }`}
      >
        {left.map((pin) => (
          <PinRow key={pin.id} pin={pin} side="left" compact={compact} />
        ))}
      </div>

      <div
        className={`absolute right-4 top-5 ${
          isArduino ? "w-[96px] space-y-1" : "w-[86px] space-y-2"
        }`}
      >
        {right.map((pin) => (
          <PinRow key={pin.id} pin={pin} side="right" compact={compact} />
        ))}
      </div>

      {isArduino && (
        <div className="absolute bottom-4 left-1/2 h-8 w-20 -translate-x-1/2 rounded-md border-2 border-black bg-gray-300 text-center text-[10px] leading-7 text-black">
          USB
        </div>
      )}
    </div>
  );
}