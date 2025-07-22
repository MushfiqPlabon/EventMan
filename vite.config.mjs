import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "path"; // Import resolve for absolute paths

export default defineConfig({
  plugins: [tailwindcss()],
  // No 'root' here if we're using absolute paths for input
  // root: 'static', // Removed root to use absolute paths in input for clarity

  build: {
    manifest: true,
    outDir: "static/dist", // Explicitly define output directory relative to project root
    rollupOptions: {
      input: {
        // Define named entry points using absolute paths for robustness
        main_css: resolve(__dirname, "static/src/input.css"),
        toggle_js: resolve(__dirname, "static/src/js/toggle.js"),
      },
      output: {
        // Ensure output filenames are predictable and match Django's static tag expectations
        entryFileNames: "[name].js", // For JS entry points (e.g., toggle_js.js)
        assetFileNames: (assetInfo) => {
          // For CSS and other assets
          if (assetInfo.name.endsWith(".css")) {
            return "[name].css"; // For CSS (e.g., main_css.css)
          }
          return "[name].[ext]"; // For other assets
        },
      },
    },
  },
});
