import { detectPlatform } from "./detectors";
import { detectGrowwStock } from "./platforms/groww";

const platform = detectPlatform();

console.log(`[FinVisor] Platform detected: ${platform}`);

if (platform === "groww") {
  const stock = detectGrowwStock();

  console.log(`[FinVisor] Stock detected: ${stock ?? "none"}`);
}
