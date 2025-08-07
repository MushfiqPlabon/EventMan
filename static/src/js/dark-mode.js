
document.addEventListener('DOMContentLoaded', () => {
  const darkModeToggle = document.getElementById('darkModeToggle');
  const userTheme = localStorage.getItem('theme');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;

  function updateToggleButtonEmoji() {
    if (document.documentElement.classList.contains('dark')) {
      darkModeToggle.textContent = '☀️'; // Sun emoji for dark mode
    } else {
      darkModeToggle.textContent = '🌙'; // Moon emoji for light mode
    }
  }

  // Check theme on initial load
  if (userTheme === 'dark' || (!userTheme && systemTheme)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  // Update emoji on initial load
  updateToggleButtonEmoji();

  // Toggle theme and update emoji on click
  darkModeToggle.addEventListener('click', () => {
    const isDarkMode = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    updateToggleButtonEmoji(); // Update emoji after toggling
  });
});
