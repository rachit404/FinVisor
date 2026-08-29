import { detectPlatform } from "./detectors";
import { extractGrowwPageContext } from "./platforms/groww";
import { watchNavigation } from "./navigation";
import { sendStockContext } from "../shared/api";

function detectCurrentPage() {
  const platform = detectPlatform();

  console.log("[FinVisor] Platform:", platform);

  if (platform === "groww") {
    const context = extractGrowwPageContext();

    if (context) {
      console.log("[FinVisor] StockPageContext:", context);

      sendStockContext(context)
        .then((response) => {
          console.log("[FinVisor] Backend response:", response);
        })
        .catch((error) => {
          console.error("[FinVisor] Backend request failed:", error);
        });
    } else {
      console.log("[FinVisor] No Groww stock detected");
    }

    return;
  }

  console.log("[FinVisor] Unsupported platform");
}

console.log("[FinVisor] Content script initialized");

detectCurrentPage();

watchNavigation((url) => {
  console.log("[FinVisor] Navigation detected:", url);
  detectCurrentPage();
});
