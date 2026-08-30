import type { StockPageContext } from "../content/context";

export type StockContextBackendResponse = {
  success: boolean;
  data?: unknown;
  error?: string;
};

export type CurrentStockContextResponse = {
  success: boolean;
  context?: StockPageContext;
  backendData?: unknown;
  error?: string;
};

export function sendStockContext(
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

export function getCurrentStockContext(): Promise<CurrentStockContextResponse> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      {
        type: "FINVISOR_GET_CURRENT_STOCK_CONTEXT",
      },
      (response: CurrentStockContextResponse) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        resolve(response);
      },
    );
  });
}
