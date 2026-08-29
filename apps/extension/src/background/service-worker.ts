type ApiRequest = {
  type: "FINVISOR_SEND_STOCK_CONTEXT";
  context: unknown;
};

const API_BASE_URL = "http://127.0.0.1:5000";

chrome.runtime.onMessage.addListener(
  (message: ApiRequest, _sender, sendResponse) => {
    if (message?.type !== "FINVISOR_SEND_STOCK_CONTEXT") {
      return;
    }

    fetch(`${API_BASE_URL}/api/context`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message.context),
    })
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data?.error || `Backend returned HTTP ${response.status}`,
          );
        }

        sendResponse({
          success: true,
          data,
        });
      })
      .catch((error) => {
        console.error("[FinVisor] Backend request failed:", error);

        sendResponse({
          success: false,
          error: error instanceof Error ? error.message : String(error),
        });
      });

    return true;
  },
);

console.log("[FinVisor] Background service worker started.");
