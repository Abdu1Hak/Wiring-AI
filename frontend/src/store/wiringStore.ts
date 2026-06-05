import { create } from "zustand";
import type { Edge, Node } from "@xyflow/react";

import { fetchComponents, generatePlan } from "@/lib/api";
import type {
  CompatibilityFinding,
  ComponentSummary,
  PlanResponse,
  WiringStep,
} from "@/types/wiring";

type WiringState = {
  catalog: ComponentSummary[];
  selectedIds: string[];
  projectDescription: string;
  searchQuery: string;
  loading: boolean;
  planStatus: string | null;
  projectTitle: string;
  projectSummary: string;
  compatibilityFindings: CompatibilityFinding[];
  nodes: Node[];
  edges: Edge[];
  steps: WiringStep[];
  warnings: string[];
  assumptions: string[];
  fallbackMessage: string | null;
  loadCatalog: () => Promise<void>;
  setProjectDescription: (value: string) => void;
  setSearchQuery: (value: string) => void;
  toggleComponent: (id: string) => void;
  removeComponent: (id: string) => void;
  generateWiring: () => Promise<void>;
};

function edgesFromPlan(plan: PlanResponse): Edge[] {
  return plan.graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.sourceHandle,
    targetHandle: edge.targetHandle,
    label: edge.label,
    type: edge.type ?? "smoothstep",
    style: {
      stroke: edge.data?.wireColor
        ? {
            red: "#ef4444",
            black: "#1f2937",
            blue: "#3b82f6",
            green: "#22c55e",
            white: "#9ca3af",
            teal: "#14b8a6",
            yellow: "#eab308",
          }[edge.data.wireColor] ?? "#3b82f6"
        : "#3b82f6",
      strokeWidth: 2,
    },
    data: edge.data,
  }));
}

export const useWiringStore = create<WiringState>((set, get) => ({
  catalog: [],
  selectedIds: [],
  projectDescription: "",
  searchQuery: "",
  loading: false,
  planStatus: null,
  projectTitle: "",
  projectSummary: "",
  compatibilityFindings: [],
  nodes: [],
  edges: [],
  steps: [],
  warnings: [],
  assumptions: [],
  fallbackMessage: null,

  loadCatalog: async () => {
    const catalog = await fetchComponents();
    set({ catalog });
  },

  setProjectDescription: (value) => set({ projectDescription: value }),
  setSearchQuery: (value) => set({ searchQuery: value }),

  toggleComponent: (id) =>
    set((state) => ({
      selectedIds: state.selectedIds.includes(id)
        ? state.selectedIds.filter((item) => item !== id)
        : [...state.selectedIds, id],
    })),

  removeComponent: (id) =>
    set((state) => ({
      selectedIds: state.selectedIds.filter((item) => item !== id),
    })),

  generateWiring: async () => {
    const { projectDescription, selectedIds } = get();
    set({ loading: true, fallbackMessage: null });
    try {
      const plan = await generatePlan(projectDescription, selectedIds);
      set({
        planStatus: plan.status,
        projectTitle: plan.projectTitle,
        projectSummary: plan.projectSummary,
        compatibilityFindings: plan.compatibilityFindings,
        nodes: plan.graph.nodes as Node[],
        edges: plan.aiPlanAccepted ? edgesFromPlan(plan) : [],
        steps: plan.steps,
        warnings: plan.warnings,
        assumptions: plan.assumptions,
        fallbackMessage: plan.fallbackMessage ?? null,
      });
    } finally {
      set({ loading: false });
    }
  },
}));
