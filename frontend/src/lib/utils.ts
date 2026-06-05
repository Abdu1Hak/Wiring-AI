import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const WIRE_COLORS: Record<string, string> = {
  red: "#ef4444",
  orange: "#f97316",
  black: "#1f2937",
  blue: "#3b82f6",
  purple: "#a855f7",
  green: "#22c55e",
  teal: "#14b8a6",
  yellow: "#eab308",
  gray: "#6b7280",
  pink: "#ec4899",
  brown: "#92400e",
  white: "#e5e7eb",
};
