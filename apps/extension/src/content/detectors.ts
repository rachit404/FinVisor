export type Platform = "groww" | "zerodha" | "screener" | "unknown";

export function detectPlatform(): Platform {
  const hostname = window.location.hostname;

  if (hostname.endsWith("groww.in")) {
    return "groww";
  }

  if (hostname.endsWith("zerodha.com")) {
    return "zerodha";
  }

  if (hostname.endsWith("screener.in")) {
    return "screener";
  }

  return "unknown";
}
