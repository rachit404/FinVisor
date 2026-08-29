import type { StockPageContext } from "../content/context";

export function sendStockContext(context: StockPageContext): Promise<{
  success: boolean;
  data?: unknown;
  error?: string;
}> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      {
        type: "FINVISOR_SEND_STOCK_CONTEXT",
        context,
      },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        resolve(response);
      },
    );
  });
}
