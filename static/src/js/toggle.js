const darkModeToggle = document.getElementById("darkModeToggle");
const htmlElement = document.documentElement; // This is the <html> tag

// Check for saved theme preference or system preference
try {
  const savedTheme = localStorage.getItem("theme");
  if (
    savedTheme === "dark" ||
    (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    htmlElement.classList.add("dark");
  } else {
    // Explicitly remove 'dark' class for light theme or no preference
    htmlElement.classList.remove("dark");
  }
} catch (e) {
  console.warn("Could not set initial theme due to an error:", e);
}

// Add click listener only if the toggle element actually exists on the page.
if (darkModeToggle) {
  darkModeToggle.addEventListener("click", () => {
    try {
      const isDarkMode = htmlElement.classList.toggle("dark");
      localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    } catch (e) {
      console.warn("Could not save theme preference to localStorage:", e);
    }
  });
}