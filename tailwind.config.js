/** @type {import('tailwindcss').Config} */
export const darkMode = "class";

export const content = [
  "./templates/**/*.{html,py}", // Look for HTML files in a 'templates' folder at the project root
  "./**/templates/**/*.{html,py}", // Look for HTML files in the 'events' app's templates folder
  "./static/src/js/**/*.js",
];

export const theme = {
  extend: {},
};

export const plugins = [];
