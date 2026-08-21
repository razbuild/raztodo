/**
 * Priority picker – custom in-field selector replacing native <select>.
 *
 * Values cycle through: "" → "L" → "M" → "H" (and back).
 * The hidden <input id="..."> keeps the machine value so existing
 * actions.js / edit.js code reads `.value` unchanged.
 *
 * Wire once at app startup by calling initPriorityPickers().
 * Works on dynamically rendered pickers via event delegation on document.
 */

const STEPS = [
  { value: "", label: "None" },
  { value: "L", label: "Low" },
  { value: "M", label: "Medium" },
  { value: "H", label: "High" },
];

function stepIndex(value) {
  const idx = STEPS.findIndex((s) => s.value === value);
  return idx === -1 ? 0 : idx;
}

function applyStep(pickerId, delta) {
  const input = document.getElementById(pickerId);
  const labelEl = document.querySelector(`[data-picker-label="${pickerId}"]`);
  if (!input || !labelEl) return;

  const current = stepIndex(input.value);
  const next = Math.min(Math.max(current + delta, 0), STEPS.length - 1);
  const step = STEPS[next];

  input.value = step.value;
  labelEl.textContent = step.label;

  // Update aria-label on arrow buttons to reflect boundary state
  const picker = input.closest(".priority-picker");
  if (picker) {
    const [prevBtn, nextBtn] = picker.querySelectorAll(".priority-arrow");
    if (prevBtn) prevBtn.disabled = next === 0;
    if (nextBtn) nextBtn.disabled = next === STEPS.length - 1;
  }
}

/** Reset a picker back to "None". */
export function resetPicker(pickerId) {
  const input = document.getElementById(pickerId);
  const labelEl = document.querySelector(`[data-picker-label="${pickerId}"]`);
  if (!input || !labelEl) return;
  input.value = "";
  labelEl.textContent = "None";
  const picker = input.closest(".priority-picker");
  if (picker) {
    const [prevBtn, nextBtn] = picker.querySelectorAll(".priority-arrow");
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = false;
  }
}

/**
 * Wire all priority pickers via a single delegated listener on `document`.
 * Call once from app.js after DOMContentLoaded.
 */
export function initPriorityPickers() {
  // Set initial boundary state for any pickers already in the DOM.
  document.querySelectorAll(".priority-picker").forEach((picker) => {
    const input = picker.querySelector("input[type=hidden]");
    if (!input) return;
    const idx = stepIndex(input.value);
    const [prevBtn, nextBtn] = picker.querySelectorAll(".priority-arrow");
    if (prevBtn) prevBtn.disabled = idx === 0;
    if (nextBtn) nextBtn.disabled = idx === STEPS.length - 1;
  });

  // Delegated click handler – works for dynamically rendered pickers too.
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".priority-arrow[data-picker]");
    if (!btn) return;
    const pickerId = btn.dataset.picker;
    const dir = parseInt(btn.dataset.dir, 10);
    applyStep(pickerId, dir);
  });

  // Keyboard: left/right arrows on the picker group itself.
  document.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    const picker = e.target.closest(".priority-picker");
    if (!picker) return;
    const input = picker.querySelector("input[type=hidden]");
    if (!input) return;
    e.preventDefault();
    applyStep(input.id, e.key === "ArrowRight" ? 1 : -1);
  });
}
