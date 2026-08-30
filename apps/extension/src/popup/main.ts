import { getCurrentStockContext } from "../shared/api";

const statusElement = document.querySelector<HTMLDivElement>("#status");

const stockContextElement =
  document.querySelector<HTMLDivElement>("#stock-context");

async function loadStockContext(): Promise<void> {
  if (!statusElement || !stockContextElement) {
    return;
  }

  try {
    const response = await getCurrentStockContext();

    if (!response.success || !response.context) {
      statusElement.textContent = response.error ?? "No stock context found.";

      return;
    }

    const context = response.context;

    statusElement.textContent = "Stock context found.";

    stockContextElement.innerHTML = `
      <h2>${context.companyName ?? context.symbol}</h2>

      <p>
        <strong>Symbol:</strong>
        ${context.symbol}
      </p>

      <p>
        <strong>Exchange:</strong>
        ${context.exchange ?? "Unknown"}
      </p>

      <p>
        <strong>Price:</strong>
        ${context.price ?? "Unavailable"}
      </p>

      <p>
        <strong>Change:</strong>
        ${context.change ?? "Unavailable"}
      </p>

      <p>
        <strong>Change %:</strong>
        ${context.changePercent ?? "Unavailable"}
      </p>
    `;
  } catch (error) {
    statusElement.textContent =
      error instanceof Error ? error.message : "Unable to load stock context.";
  }
}

void loadStockContext();
