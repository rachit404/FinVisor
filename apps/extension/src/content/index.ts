import { detectPlatform } from "./detectors";
import { extractGrowwPageContext } from "./platforms/groww";
import { watchNavigation } from "./navigation";
import type { StockPageContext } from "./context";

type StockContextBackendResponse = {
  success: boolean;
  data?: unknown;
  error?: string;
};

function sendStockContext(
  context: StockPageContext,
): Promise<StockContextBackendResponse> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      {
        type: "FINVISOR_SEND_STOCK_CONTEXT",
        context,
      },
      (response: StockContextBackendResponse) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        resolve(response);
      },
    );
  });
}

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
