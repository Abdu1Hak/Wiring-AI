import { BaseComponentNode } from "./BaseComponentNode";

const shared = { default: BaseComponentNode };

export const nodeTypes = {
  arduinoUnoNode: BaseComponentNode,
  arduinoNanoNode: BaseComponentNode,
  esp32Node: BaseComponentNode,
  genericControllerNode: BaseComponentNode,
  ultrasonicSensorNode: BaseComponentNode,
  dhtSensorNode: BaseComponentNode,
  pirSensorNode: BaseComponentNode,
  genericSensorNode: BaseComponentNode,
  ledNode: BaseComponentNode,
  rgbLedNode: BaseComponentNode,
  buzzerNode: BaseComponentNode,
  servoNode: BaseComponentNode,
  motorNode: BaseComponentNode,
  displayNode: BaseComponentNode,
  resistorNode: BaseComponentNode,
  transistorNode: BaseComponentNode,
  diodeNode: BaseComponentNode,
  driverModuleNode: BaseComponentNode,
  breadboardNode: BaseComponentNode,
  genericComponentNode: BaseComponentNode,
  ...shared,
};
