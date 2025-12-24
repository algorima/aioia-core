import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";
import pkg from "./package.json" with { type: "json" };

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  build: {
    sourcemap: true,
    lib: {
      entry: {
        index: resolve(__dirname, "src/index.ts"),
        client: resolve(__dirname, "src/client.ts"),
      },
      formats: ["es", "cjs"],
      fileName: (format, entryName) =>
        `${entryName}.${format === "es" ? "js" : "cjs"}`,
    },
    rollupOptions: {
      external: [
        // Automatically externalize peerDependencies
        ...Object.keys(pkg.peerDependencies || {}),
        // Automatically externalize dependencies (they install but don't bundle)
        ...Object.keys(pkg.dependencies || {}),
        // Add peer submodules explicitly
        /^next\//,
      ],
      output: {
        banner: (chunk) => {
          // Only add 'use client' to client entry point
          if (chunk.name === "client") {
            return '"use client";';
          }
          return "";
        },
      },
    },
  },
  plugins: [dts()],
});
