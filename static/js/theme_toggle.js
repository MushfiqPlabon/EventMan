// events/static/js/theme_toggle.js

const themeToggleBtn = document.getElementById("theme-toggle");
const htmlElement = document.documentElement; // This targets the <html> tag

// Function to set the theme class on the HTML element
function setTheme(theme) {
  if (theme === "dark") {
    htmlElement.classList.add("dark");
    localStorage.setItem("theme", "dark");
  } else {
    htmlElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
  }
}

// Function to get the theme preference
function getThemePreference() {
  // 1. Check localStorage first
  const storedTheme = localStorage.getItem("theme");
  if (storedTheme) {
    return storedTheme;
  }
  // 2. If no localStorage, check system preference
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    return "dark";
  }
  // 3. Default to light
  return "light";
}

// Apply initial theme on page load
const initialTheme = getThemePreference();
setTheme(initialTheme);

// Add event listener for the toggle button
if (themeToggleBtn) {
  themeToggleBtn.addEventListener("click", () => {
    if (htmlElement.classList.contains("dark")) {
      setTheme("light");
    } else {
      setTheme("dark");
    }
  });
}