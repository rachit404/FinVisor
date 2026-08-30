import { getCurrentStockContext } from "../shared/api";

const statusElement = document.querySelector<HTMLParagraphElement>("#status");

const stockElement = document.querySelector<HTMLElement>("#stock");

const companyNameElement =
  document.querySelector<HTMLHeadingElement>("#company-name");

const symbolElement = document.querySelector<HTMLSpanElement>("#symbol");

const exchangeElement = document.querySelector<HTMLSpanElement>("#exchange");

const priceElement = document.querySelector<HTMLSpanElement>("#price");

const changeElement = document.querySelector<HTMLSpanElement>("#change");

async function loadCurrentStock(): Promise<void> {
  if (
    !statusElement ||
    !stockElement ||
    !companyNameElement ||
    !symbolElement ||
    !exchangeElement ||
    !priceElement ||
    !changeElement
  ) {
    return;
  }

  try {
    const response = await getCurrentStockContext();

    if (!response.success || !response.context) {
      statusElement.textContent =
        response.error ?? "No stock detected on this page.";

      return;
    }

    const { context } = response;

    companyNameElement.textContent = context.companyName ?? context.symbol;

    symbolElement.textContent = context.symbol;

    exchangeElement.textContent = context.exchange ?? "Unknown";

    priceElement.textContent =
      context.price !== null ? `₹${context.price}` : "Unavailable";

    if (context.change !== null && context.changePercent !== null) {
      changeElement.textContent = `${context.change} (${context.changePercent}%)`;
    } else {
      changeElement.textContent = "Unavailable";
    }

    statusElement.hidden = true;
    stockElement.hidden = false;
  } catch (error) {
    statusElement.textContent =
      error instanceof Error ? error.message : "Failed to load stock context.";
  }
}

void loadCurrentStock();
