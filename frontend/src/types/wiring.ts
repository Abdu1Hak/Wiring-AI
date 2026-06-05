export type ComponentPin = {
  pinId: string;
  label: string;
  handleId: string;
  pinType: string;
  position: "left" | "right" | "top" | "bottom";
  direction?: string;
};

export type ComponentNodeData = {
  componentId: string;
  label: string;
  category: string;
  pins: ComponentPin[];
};

export type ComponentSummary = {
  id: string;
  name: string;
  category: string;
  frontendNodeType: string;
};

export type CompatibilityFinding = {
  type: string;
  severity: "info" | "warning" | "blocking";
  message: string;
  affectedComponentIds?: string[];
  recommendedComponentIds?: string[];
};

export type WiringStep = {
  stepNumber: number;
  title: string;
  instruction: string;
  relatedConnectionIds: string[];
  safetyNote?: string | null;
};

export type PlanResponse = {
  status: string;
  projectTitle: string;
  projectSummary: string;
  aiPlanAccepted: boolean;
  compatibilityFindings: CompatibilityFinding[];
  graph: {
    nodes: Array<{
      id: string;
      type: string;
      position: { x: number; y: number };
      data: ComponentNodeData;
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      sourceHandle: string;
      targetHandle: string;
      label?: string;
      type?: string;
      data?: {
        wireColor?: string;
        purpose?: string;
        connectionType?: string;
      };
    }>;
  };
  steps: WiringStep[];
  warnings: string[];
  assumptions: string[];
  fallbackMessage?: string | null;
};
