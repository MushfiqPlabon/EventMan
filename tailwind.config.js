// tailwind.config.js
/** @type {import('tailwindcss').Config} */

export const darkMode = "class"; // Enable dark mode support

export const content = [
    "./templates/**/*.{html,py}", // Look for HTML files in a 'templates' folder at the project root
    "./**/templates/**/*.{html,py}", // Look for HTML files in the 'events' app's templates folder
    // Add other app template paths if you create more apps, e.g., "./your_other_app/templates/**/*.html",
];
export const theme = {
    extend: {},
};
export const plugins = [];
