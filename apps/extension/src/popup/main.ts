import { analyzeStock, getCurrentStockContext } from "../shared/api";

const statusElement = document.querySelector<HTMLDivElement>("#status");

const stockContextElement =
  document.querySelector<HTMLDivElement>("#stock-context");

const questionElement =
  document.querySelector<HTMLTextAreaElement>("#question");

const askButtonElement =
  document.querySelector<HTMLButtonElement>("#ask-button");

const answerElement = document.querySelector<HTMLDivElement>("#answer");

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

async function handleAsk(): Promise<void> {
  const question = questionElement?.value.trim();

  if (!question) {
    if (answerElement) {
      answerElement.textContent = "Please enter a question.";
    }

    return;
  }

  if (askButtonElement) {
    askButtonElement.disabled = true;
  }

  if (answerElement) {
    answerElement.textContent = "Analyzing stock...";
  }

  try {
    const response = await analyzeStock(question);

    if (!response.success || !response.data) {
      throw new Error(response.error ?? "Unable to analyze stock.");
    }

    const analysis = response.data;

    if (answerElement) {
      answerElement.innerHTML = `
        <h3>Analysis</h3>

        <p>
          <strong>Action:</strong>
          ${analysis.action}
        </p>

        <p>
          <strong>Confidence:</strong>
          ${analysis.confidence}%
        </p>

        <p>
          <strong>Summary:</strong>
          ${analysis.summary}
        </p>

        <strong>Reasons:</strong>

        <ul>
          ${analysis.reasons.map((reason) => `<li>${reason}</li>`).join("")}
        </ul>
      `;
    }
  } catch (error) {
    if (answerElement) {
      answerElement.textContent =
        error instanceof Error ? error.message : "Unable to analyze stock.";
    }
  } finally {
    if (askButtonElement) {
      askButtonElement.disabled = false;
    }
  }
}

void loadStockContext();

askButtonElement?.addEventListener("click", () => {
  void handleAsk();
});
