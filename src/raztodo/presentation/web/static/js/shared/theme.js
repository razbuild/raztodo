const THEME_KEY = "theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);

  const button = document.getElementById("theme-toggle");
  if (button) {
    button.textContent = theme === "dark" ? "🌙" : "☀️";
  }
}

function toggleTheme() {
  const current =
    document.documentElement.getAttribute("data-theme") || "dark";

  const next = current === "dark" ? "light" : "dark";

  applyTheme(next);

  localStorage.setItem(THEME_KEY, next);
}

export function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
  applyTheme(savedTheme);

  document
    .getElementById("theme-toggle")
    ?.addEventListener("click", toggleTheme);
}
