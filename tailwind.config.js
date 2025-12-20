/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./templates/**/*.html",
		"./static/src/**/*.js",
		// Add any other paths where you use Tailwind classes
	],
	theme: {
		extend: {
			screens: {
				mobile: "480px",
				// Add custom breakpoints here if needed
			},
		},
	},
	plugins: [],
	darkMode: "class", // This enables dark mode with a class
};
