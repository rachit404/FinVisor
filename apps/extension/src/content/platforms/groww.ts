export function detectGrowwStock(): string | null {
  const path = window.location.pathname;

  const match = path.match(/\/stocks\/([^/]+)/);

  if (!match) {
    return null;
  }

  return match[1].toUpperCase();
}
