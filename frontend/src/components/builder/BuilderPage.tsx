"use client";

import { useEffect, useMemo } from "react";

import WiringDiagram from "@/components/flow/WiringDiagram";
import { cn } from "@/lib/utils";
import { useWiringStore } from "@/store/wiringStore";

const statusLabels: Record<string, { label: string; className: string }> = {
  success: { label: "Compatible", className: "bg-emerald-100 text-emerald-800" },
  compatible_with_warnings: {
    label: "Compatible with warnings",
    className: "bg-yellow-100 text-yellow-800",
  },
  missing_required_components: {
    label: "Missing required components",
    className: "bg-orange-100 text-orange-800",
  },
  incompatible: { label: "Incompatible", className: "bg-red-100 text-red-800" },
  unsafe_blocked: { label: "Safety blocked", className: "bg-red-200 text-red-900" },
  needs_more_info: { label: "Needs more info", className: "bg-slate-100 text-slate-800" },
  no_valid_plan: { label: "No valid plan", className: "bg-red-100 text-red-800" },
};

export default function BuilderPage() {
  const catalog = useWiringStore((s) => s.catalog);
  const selectedIds = useWiringStore((s) => s.selectedIds);
  const projectDescription = useWiringStore((s) => s.projectDescription);
  const searchQuery = useWiringStore((s) => s.searchQuery);
  const loading = useWiringStore((s) => s.loading);
  const planStatus = useWiringStore((s) => s.planStatus);
  const projectTitle = useWiringStore((s) => s.projectTitle);
  const projectSummary = useWiringStore((s) => s.projectSummary);
  const compatibilityFindings = useWiringStore((s) => s.compatibilityFindings);
  const steps = useWiringStore((s) => s.steps);
  const warnings = useWiringStore((s) => s.warnings);
  const assumptions = useWiringStore((s) => s.assumptions);
  const fallbackMessage = useWiringStore((s) => s.fallbackMessage);
  const nodes = useWiringStore((s) => s.nodes);

  const loadCatalog = useWiringStore((s) => s.loadCatalog);
  const setProjectDescription = useWiringStore((s) => s.setProjectDescription);
  const setSearchQuery = useWiringStore((s) => s.setSearchQuery);
  const toggleComponent = useWiringStore((s) => s.toggleComponent);
  const removeComponent = useWiringStore((s) => s.removeComponent);
  const generateWiring = useWiringStore((s) => s.generateWiring);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const selectedComponents = useMemo(
    () => catalog.filter((c) => selectedIds.includes(c.id)),
    [catalog, selectedIds]
  );

  const filteredCatalog = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q)
    );
  }, [catalog, searchQuery]);

  const statusBadge = planStatus ? statusLabels[planStatus] : null;

  return (
    <main className="mx-auto max-w-7xl space-y-6 p-6">
      <header className="rounded-xl bg-zinc-950 px-5 py-4">
        <h1 className="text-3xl font-bold tracking-tight text-white">Wiring AI</h1>
        <p className="mt-2 max-w-2xl text-zinc-300">
          Beginner-friendly electronics wiring assistant. Select catalog components,
          describe your project, and get a verified pin-level diagram with steps.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        <aside className="space-y-4">
          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-zinc-900">Project description</h2>
            <textarea
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              placeholder="Example: Arduino distance sensor that turns on an LED when close"
              className="mt-2 min-h-[100px] w-full rounded-lg border px-3 py-2 text-sm text-black placeholder:text-zinc-400"
            />
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-zinc-900">Component search</h2>
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search catalog..."
              className="mt-2 w-full rounded-lg border px-3 py-2 text-sm text-black placeholder:text-zinc-400"
            />
            <div className="mt-3 max-h-56 space-y-1 overflow-y-auto">
              {filteredCatalog.map((component) => {
                const isSelected = selectedIds.includes(component.id);
                return (
                  <button
                    key={component.id}
                    type="button"
                    onClick={() => toggleComponent(component.id)}
                    className={cn(
                      "flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm",
                      isSelected
                        ? "bg-zinc-900 text-white"
                        : "text-zinc-900 hover:bg-zinc-100"
                    )}
                  >
                    <span>{component.name}</span>
                    <span
                      className={cn(
                        "text-xs",
                        isSelected ? "text-zinc-300" : "text-zinc-600"
                      )}
                    >
                      {component.category}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-zinc-900">Selected components</h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {selectedComponents.length === 0 && (
                <p className="text-sm text-zinc-500">No components selected yet.</p>
              )}
              {selectedComponents.map((component) => (
                <button
                  key={component.id}
                  type="button"
                  onClick={() => removeComponent(component.id)}
                  className="rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-800 hover:bg-zinc-200"
                  title="Click to remove"
                >
                  {component.name} ×
                </button>
              ))}
            </div>
            <button
              type="button"
              disabled={selectedIds.length === 0 || loading}
              onClick={() => generateWiring()}
              className="mt-4 w-full rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-zinc-400"
            >
              {loading ? "Generating..." : "Generate Wiring"}
            </button>
          </section>
        </aside>

        <div className="space-y-4">
          {(planStatus || compatibilityFindings.length > 0) && (
            <section className="rounded-xl border bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-sm font-semibold text-zinc-900">Compatibility</h2>
                {statusBadge && (
                  <span className={cn("rounded-full px-3 py-1 text-xs font-medium", statusBadge.className)}>
                    {statusBadge.label}
                  </span>
                )}
              </div>
              {projectTitle && <p className="mt-2 font-medium text-zinc-900">{projectTitle}</p>}
              {projectSummary && <p className="mt-1 text-sm text-zinc-600">{projectSummary}</p>}
              {fallbackMessage && (
                <p className="mt-2 rounded-lg bg-red-50 p-3 text-sm text-red-800">{fallbackMessage}</p>
              )}
              {compatibilityFindings.length > 0 && (
                <ul className="mt-3 space-y-2">
                  {compatibilityFindings.map((finding, index) => (
                    <li
                      key={`${finding.type}-${index}`}
                      className={cn(
                        "rounded-lg p-3 text-sm",
                        finding.severity === "blocking" && "bg-red-50 text-red-900",
                        finding.severity === "warning" && "bg-yellow-50 text-yellow-900",
                        finding.severity === "info" && "bg-blue-50 text-blue-900"
                      )}
                    >
                      {finding.message}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}

          <section className="rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-sm font-semibold text-zinc-900">Wiring diagram</h2>
            {nodes.length > 0 ? (
              <WiringDiagram />
            ) : (
              <div className="flex h-[480px] items-center justify-center rounded-xl border border-dashed bg-zinc-50 text-sm text-zinc-500">
                Generate wiring to see the verified diagram.
              </div>
            )}
          </section>

          {steps.length > 0 && (
            <section className="rounded-xl border bg-white p-4 shadow-sm">
              <h2 className="text-sm font-semibold text-zinc-900">Wiring steps</h2>
              <ol className="mt-3 space-y-3">
                {steps.map((step) => (
                  <li key={step.stepNumber} className="rounded-lg bg-zinc-50 p-3">
                    <div className="font-medium text-zinc-900">
                      {step.stepNumber}. {step.title}
                    </div>
                    <p className="mt-1 text-sm text-zinc-600">{step.instruction}</p>
                    {step.safetyNote && (
                      <p className="mt-1 text-xs text-amber-700">{step.safetyNote}</p>
                    )}
                  </li>
                ))}
              </ol>
            </section>
          )}

          {(warnings.length > 0 || assumptions.length > 0) && (
            <section className="grid gap-4 md:grid-cols-2">
              {warnings.length > 0 && (
                <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4">
                  <h2 className="text-sm font-semibold text-yellow-900">Warnings</h2>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-yellow-900">
                    {warnings.map((w) => (
                      <li key={w}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
              {assumptions.length > 0 && (
                <div className="rounded-xl border bg-white p-4 shadow-sm">
                  <h2 className="text-sm font-semibold text-zinc-900">Assumptions</h2>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-600">
                    {assumptions.map((a) => (
                      <li key={a}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}
        </div>
      </div>
    </main>
  );
}
