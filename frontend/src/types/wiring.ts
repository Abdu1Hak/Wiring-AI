export type PinType =
  | "power_out"
  | "power_in"
  | "ground"
  | "digital_io"
  | "signal"
  | "passive";

export type Pin = {
  id: string;
  label: string;
  type: PinType;
};

export type ComponentDef = {
  id: string;
  name: string;
  category: string;
  pins: Pin[];
};