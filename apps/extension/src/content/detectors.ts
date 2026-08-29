import { detectGrowwStock } from "./platforms/groww";

export type Platform = "groww" | "zerodha" | "screener" | "unknown";

export function detectPlatform(): Platform {
  const hostname = window.location.hostname;

  if (hostname.includes("groww.in")) {
    return "groww";
  }

  if (hostname.includes("zerodha.com")) {
    return "zerodha";
  }

  if (hostname.includes("screener.in")) {
    return "screener";
  }

  return "unknown";
}

export function detectStock() {
  const platform = detectPlatform();

  switch (platform) {
    case "groww":
      return detectGrowwStock();

    default:
      return null;
  }
}
