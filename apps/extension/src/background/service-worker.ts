import type { StockPageContext } from "../content/context";
import type { AnalysisResponse } from "../shared/types";

type SendStockContextMessage = {
  type: "FINVISOR_SEND_STOCK_CONTEXT";
  context: StockPageContext;
};

type GetCurrentStockContextMessage = {
  type: "FINVISOR_GET_CURRENT_STOCK_CONTEXT";
};

type AnalyzeStockMessage = {
  type: "FINVISOR_ANALYZE_STOCK";
  prompt: string;
};

type ExtensionMessage =
  | SendStockContextMessage
  | GetCurrentStockContextMessage
  | AnalyzeStockMessage;

type StoredStockContext = {
  context: StockPageContext;
  backendData: unknown;
  updatedAt: string;
};

type StoredContexts = Record<string, StoredStockContext>;

type SnapshotResponse = {
  snapshot_hash: string;
};

const API_BASE_URL = "http://127.0.0.1:8000";

const STOCK_CONTEXT_STORAGE_KEY = "finvisor_stock_context_by_tab";

async function saveStockContext(
  tabId: number,
  context: StockPageContext,
  backendData: unknown,
): Promise<void> {
  const stored = await chrome.storage.local.get(STOCK_CONTEXT_STORAGE_KEY);

  const contexts = (stored[STOCK_CONTEXT_STORAGE_KEY] ?? {}) as StoredContexts;

  contexts[String(tabId)] = {
    context,
    backendData,
    updatedAt: new Date().toISOString(),
  };

  await chrome.storage.local.set({
    [STOCK_CONTEXT_STORAGE_KEY]: contexts,
  });
}

async function getCurrentTabId(): Promise<number | null> {
  const tabs = await chrome.tabs.query({
    active: true,
    currentWindow: true,
  });

  const tabId = tabs[0]?.id;

  return typeof tabId === "number" ? tabId : null;
}

async function getStoredStockContext(
  tabId: number,
): Promise<StoredStockContext | null> {
  const stored = await chrome.storage.local.get(STOCK_CONTEXT_STORAGE_KEY);

  const contexts = (stored[STOCK_CONTEXT_STORAGE_KEY] ?? {}) as StoredContexts;

  return contexts[String(tabId)] ?? null;
}

async function getLatestSnapshot(
  instrumentId: string,
): Promise<SnapshotResponse> {
  const params = new URLSearchParams({
    instrument_id: instrumentId,
    interval: "1d",
  });

  const response = await fetch(
    `${API_BASE_URL}/snapshots/latest?${params.toString()}`,
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail ?? `Backend returned HTTP ${response.status}`);
  }

  return data as SnapshotResponse;
}

async function requestAnalysis(
  snapshotHash: string,
  prompt: string,
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analysis`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      snapshot_hash: snapshotHash,
      prompt,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail ?? `Backend returned HTTP ${response.status}`);
  }

  return data as AnalysisResponse;
}

chrome.runtime.onMessage.addListener(
  (message: ExtensionMessage, sender, sendResponse) => {
    if (message.type === "FINVISOR_SEND_STOCK_CONTEXT") {
      const tabId = sender.tab?.id;

      if (typeof tabId !== "number") {
        sendResponse({
          success: false,
          error: "Unable to determine source tab",
        });

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
              data?.error ??
                data?.detail ??
                `Backend returned HTTP ${response.status}`,
            );
          }

          await saveStockContext(tabId, message.context, data);

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
    }

    if (message.type === "FINVISOR_GET_CURRENT_STOCK_CONTEXT") {
      getCurrentTabId()
        .then(async (tabId) => {
          if (tabId === null) {
            sendResponse({
              success: false,
              error: "Unable to determine active tab",
            });

            return;
          }

          const stored = await getStoredStockContext(tabId);

          if (!stored) {
            sendResponse({
              success: false,
              error: "No FinVisor stock context found for this tab",
            });

            return;
          }

          sendResponse({
            success: true,
            context: stored.context,
            backendData: stored.backendData,
          });
        })
        .catch((error) => {
          sendResponse({
            success: false,
            error: error instanceof Error ? error.message : String(error),
          });
        });

      return true;
    }

    if (message.type === "FINVISOR_ANALYZE_STOCK") {
      getCurrentTabId()
        .then(async (tabId) => {
          if (tabId === null) {
            throw new Error("Unable to determine active tab");
          }

          const stored = await getStoredStockContext(tabId);

          if (!stored) {
            throw new Error("No FinVisor stock context found for this tab");
          }

          const instrumentId =
            stored.context.instrument?.instrument.instrumentId;

          if (!instrumentId) {
            throw new Error("No supported instrument found for this stock");
          }

          const snapshot = await getLatestSnapshot(instrumentId);

          const analysis = await requestAnalysis(
            snapshot.snapshot_hash,
            message.prompt,
          );

          sendResponse({
            success: true,
            data: analysis,
          });
        })
        .catch((error) => {
          console.error("[FinVisor] Analysis request failed:", error);

          sendResponse({
            success: false,
            error: error instanceof Error ? error.message : String(error),
          });
        });

      return true;
    }
  },
);

console.log("[FinVisor] Background service worker started.");
