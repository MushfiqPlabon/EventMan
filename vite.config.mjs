import { defineConfig } from "vite";
import { resolve } from "path"; // Import resolve for absolute paths

export default defineConfig({
	plugins: [],
	// No 'root' here if we're using absolute paths for input
	// root: 'static', // Removed root to use absolute paths in input for clarity

	build: {
		manifest: true,
		outDir: "static/dist", // Output to Django static dir; WhiteNoise finders and collectstatic will handle serving/copying
		rollupOptions: {
			input: {
				// Define named entry points using absolute paths for robustness
				main_css: resolve(__dirname, "static/src/input.css"),
				toggle_js: resolve(__dirname, "static/src/js/toggle.js"),
				sweetalert_js: resolve(__dirname, "static/src/js/sweetalert.js"),
				event_detail_js: resolve(__dirname, "static/src/js/event_detail.js"),
				form_enhance_js: resolve(__dirname, "static/src/js/form_enhance.js"),
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
