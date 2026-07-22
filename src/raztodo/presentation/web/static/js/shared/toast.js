import { state } from "./state.js";

export function setStatus(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = isError ? "error" : "";

  if (state.toastTimer !== null) {
    clearTimeout(state.toastTimer);
    toast.classList.remove("show");
  }

  if (!message) return;

  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add("show"));
  });

  state.toastTimer = window.setTimeout(() => {
    toast.classList.remove("show");
    state.toastTimer = null;
  }, 3000);
}
