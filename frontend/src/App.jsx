import { useEffect, useState } from "react";
import ComponentPicker from "./components/ComponentPicker";
import WiringCanvas from "./components/flow/WiringCanvas";

const API_URL = "http://localhost:8000";

export default function App() {
  const [components, setComponents] = useState([]);
  const [selected, setSelected] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [steps, setSteps] = useState([]);
  const [componentText, setComponentText] = useState("");
  const [parseMatches, setParseMatches] = useState([]);
  const [unmatched, setUnmatched] = useState([]);


  
  useEffect(() => {
    async function loadComponents() {
      const response = await fetch(`${API_URL}/components`);
      const data = await response.json();
      setComponents(data.components);
    }

    loadComponents();
  }, []);

  function toggleComponent(id) {
    setSelected((current) => {
      if (current.includes(id)) {
        return current.filter((item) => item !== id);
      }

      return [...current, id];
    });
  }

  async function generateWiring() {
    const response = await fetch(`${API_URL}/wiring/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ components: selected }),
    });

    const data = await response.json();

    setNodes(data.react_flow.nodes);
    setEdges(data.react_flow.edges);
    setWarnings(data.warnings);
    setSteps(data.steps);
  }

  async function parseComponentText() {
    const response = await fetch(`${API_URL}/components/parse`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: componentText }),
    });
  
    const data = await response.json();
  
    setParseMatches(data.matches);
    setUnmatched(data.unmatched);
  
    const matchedIds = data.matches.map((match) => match.matched_component_id);
    setSelected(matchedIds);
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wiring AI</h1>
        <p className="mt-2 text-gray-600">
          Select components and generate a basic wiring diagram.
        </p>
      </div>


      <div className="rounded-xl border bg-white p-4">
        <h2 className="mb-3 text-lg font-semibold">Type Components</h2>

        <div className="flex gap-2">
          <input
            value={componentText}
            onChange={(event) => setComponentText(event.target.value)}
            placeholder="Example: arduino, ultrasonic sensor, led, resistor"
            className="flex-1 rounded-lg border px-3 py-2 text-sm"
          />

          <button
            onClick={parseComponentText}
            className="rounded-lg bg-black px-4 py-2 text-white"
          >
            Parse
          </button>
        </div>

        {parseMatches.length > 0 && (
          <div className="mt-3 text-sm">
            <div className="font-semibold">Detected Components</div>
            <ul className="mt-1 list-disc pl-5">
              {parseMatches.map((match) => (
                <li key={match.matched_component_id}>
                  {match.name} ({Math.round(match.confidence * 100)}%)
                </li>
              ))}
            </ul>
          </div>
        )}

        {unmatched.length > 0 && (
          <div className="mt-3 rounded-lg border border-yellow-300 bg-yellow-50 p-3 text-sm">
            Could not match: {unmatched.join(", ")}
          </div>
        )}
      </div>


      <ComponentPicker
        components={components}
        selected={selected}
        onToggle={toggleComponent}
      />

      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={generateWiring}
          disabled={selected.length === 0}
          className="rounded-lg bg-black px-4 py-2 text-white disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          Generate Wiring
        </button>

        <div className="text-sm text-gray-600">
          Selected: {selected.length}
        </div>
      </div>

      {warnings.length > 0 && (
        <div className="rounded-xl border border-yellow-300 bg-yellow-50 p-4">
          <h2 className="mb-2 font-semibold">Warnings</h2>
          <ul className="list-disc space-y-1 pl-5 text-sm">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <WiringCanvas nodes={nodes} edges={edges} />

      {steps.length > 0 && (
        <div className="rounded-xl border bg-white p-4">
          <h2 className="mb-2 font-semibold">Wiring Steps</h2>
          <ol className="space-y-1 text-sm">
            {steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}

    </main>
  );
}