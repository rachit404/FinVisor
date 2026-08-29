import type { StockPageContext } from "../context";
import type { ResolvedInstrument } from "../../shared/instrument";

export type StockIdentity = {
  platform: "groww";
  symbol: string;
  exchange?: string;
  companyName?: string;
};

function parseNumber(value: string | undefined): number | null {
  if (!value) {
    return null;
  }

  const normalized = value
    .replace(/₹/g, "")
    .replace(/,/g, "")
    .replace(/%/g, "")
    .trim();

  const number = Number(normalized);

  return Number.isFinite(number) ? number : null;
}

function resolveGrowwInstrument(slug: string): ResolvedInstrument | null {
  const knownInstruments: Record<
    string,
    {
      symbol: string;
      exchange: "NSE" | "BSE";
      name: string;
    }
  > = {
    "state-bank-of-india": {
      symbol: "SBIN",
      exchange: "NSE",
      name: "State Bank of India",
    },

    "reliance-industries-ltd": {
      symbol: "RELIANCE",
      exchange: "NSE",
      name: "Reliance Industries",
    },

    "tata-consultancy-services-ltd": {
      symbol: "TCS",
      exchange: "NSE",
      name: "Tata Consultancy Services",
    },

    "hdfc-bank-ltd": {
      symbol: "HDFCBANK",
      exchange: "NSE",
      name: "HDFC Bank",
    },
  };

  const known = knownInstruments[slug];

  if (!known) {
    return null;
  }

  return {
    instrument: {
      instrumentId: `${known.exchange}:${known.symbol}`,
      symbol: known.symbol,
      exchange: known.exchange,
      name: known.name,
    },

    platformReference: {
      platform: "groww",
      platformSymbol: slug,
    },
  };
}

export function detectGrowwStock(): StockIdentity | null {
  const path = window.location.pathname;

  const match = path.match(/\/stocks\/([^/]+)/);

  if (!match) {
    return null;
  }

  const slug = decodeURIComponent(match[1]);

  return {
    platform: "groww",
    symbol: slug,
  };
}

export function extractGrowwPageContext(): StockPageContext | null {
  const identity = detectGrowwStock();

  if (!identity) {
    return null;
  }

  const bodyText = document.body.innerText;

  const priceMatch = bodyText.match(/₹\s*([\d,]+(?:\.\d+)?)/);

  const changeMatch = bodyText.match(
    /₹\s*[\d,]+(?:\.\d+)?\s+(-?[\d,]+(?:\.\d+)?)\s*\((-?[\d.]+)%\)/,
  );

  const title = document.title;

  const companyName =
    document.querySelector("h1")?.textContent?.trim() ||
    title.replace(/\s*-\s*Groww.*$/i, "").trim() ||
    undefined;

  const exchangeMatch = bodyText.match(/\b(NSE|BSE)\b/);

  const instrument = resolveGrowwInstrument(identity.symbol);

  return {
    ...identity,

    companyName,
    exchange: exchangeMatch?.[1],

    instrument,

    price: parseNumber(priceMatch?.[1]),
    change: parseNumber(changeMatch?.[1]),
    changePercent: parseNumber(changeMatch?.[2]),

    url: window.location.href,
    capturedAt: new Date().toISOString(),
  };
}
