import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        popup: "src/popup/index.html",
        background: "src/background/service-worker.ts",
        content: "src/content/index.ts",
      },
      output: {
        entryFileNames: (chunk) => {
          if (chunk.name === "background") {
            return "background.js";
          }

          if (chunk.name === "content") {
            return "content.js";
          }

          return "assets/[name].js";
        },
      },
    },
  },
});
