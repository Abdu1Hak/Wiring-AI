import type { ComponentSummary, PlanResponse } from "@/types/wiring";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchComponents(): Promise<ComponentSummary[]> {
  const response = await fetch(`${API_URL}/api/components`);
  if (!response.ok) throw new Error("Failed to load catalog");
  const data = await response.json();
  return data.components;
}

export async function generatePlan(
  projectDescription: string,
  selectedComponentIds: string[]
): Promise<PlanResponse> {
  const response = await fetch(`${API_URL}/api/ai/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      projectDescription,
      selectedComponentIds,
      mode: "generate_wiring",
    }),
  });
  if (!response.ok) throw new Error("Failed to generate wiring plan");
  return response.json();
}
