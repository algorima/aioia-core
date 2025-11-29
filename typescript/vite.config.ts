import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";
import pkg from "./package.json" with { type: "json" };

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "src/index.ts"),
      formats: ["es", "cjs"],
      fileName: (format) => `index.${format === "es" ? "js" : "cjs"}`,
    },
    rollupOptions: {
      external: [
        // Automatically externalize peerDependencies
        ...Object.keys(pkg.peerDependencies || {}),
        // Automatically externalize dependencies (they install but don't bundle)
        ...Object.keys(pkg.dependencies || {}),
        // Add peer submodules explicitly
        "react-dom",
        /^next\//,
      ],
    },
  },
  plugins: [dts()],
});
