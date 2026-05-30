import type { ComponentDef } from "../types/wiring";

type Props = {
  components: ComponentDef[];
  selected: string[];
  onToggle: (id: string) => void;
};

export default function ComponentPicker({
  components,
  selected,
  onToggle,
}: Props) {
  return (
    <div className="rounded-xl border p-4">
      <h2 className="mb-3 text-lg font-semibold">Select Components</h2>

      <div className="flex flex-wrap gap-2">
        {components.map((component) => {
          const isSelected = selected.includes(component.id);

          return (
            <button
              key={component.id}
              onClick={() => onToggle(component.id)}
              className={`rounded-full border px-4 py-2 text-sm ${
                isSelected
                  ? "bg-black text-white"
                  : "bg-white text-black hover:bg-gray-100"
              }`}
            >
              {component.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}