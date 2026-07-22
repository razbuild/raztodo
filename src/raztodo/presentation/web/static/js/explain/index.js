import { closeExplain, openExplain, switchMode } from "./modal.js";

export function initExplain() {
  window.openExplain = openExplain;

  document.getElementById("explain-backdrop").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) closeExplain();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeExplain();
  });

  document.querySelectorAll(".mode-btn").forEach((button) => {
    button.addEventListener("click", () => switchMode(button.dataset.mode));
  });

  document.querySelector(".modal-close")?.addEventListener("click", closeExplain);
}
