type NavigationCallback = (url: string) => void;

export function watchNavigation(callback: NavigationCallback): () => void {
  let lastUrl = window.location.href;

  const checkUrl = () => {
    const currentUrl = window.location.href;

    if (currentUrl === lastUrl) {
      return;
    }

    lastUrl = currentUrl;
    callback(currentUrl);
  };

  const intervalId = window.setInterval(checkUrl, 500);

  const handlePopState = () => {
    checkUrl();
  };

  window.addEventListener("popstate", handlePopState);

  return () => {
    window.clearInterval(intervalId);
    window.removeEventListener("popstate", handlePopState);
  };
}
