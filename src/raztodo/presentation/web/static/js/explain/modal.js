import { API } from "../shared/api.js";
import { state } from "../shared/state.js";
import { esc } from "../tasks/render.js";

const MODES = {
  short: "Summary",
  deep: "Deep Analysis",
  plan: "Action Plan",
};

export function openExplain(taskId) {
  const task = state.tasks.find((t) => t.id === taskId);
  state.explain.taskId = taskId;
  state.explain.mode = "short";

  document.getElementById("modal-title").textContent = task
    ? task.title
    : `Task #${taskId}`;

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === "short");
  });

  document.getElementById("explain-backdrop").classList.add("open");
  fetchExplain();
}

export function closeExplain() {
  if (state.explain.controller) {
    state.explain.controller.abort();
    state.explain.controller = null;
  }
  document.getElementById("explain-backdrop").classList.remove("open");
  state.explain.taskId = null;
}

export function switchMode(mode) {
  if (mode === state.explain.mode) return;
  if (state.explain.controller) {
    state.explain.controller.abort();
    state.explain.controller = null;
  }
  state.explain.mode = mode;
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
  fetchExplain();
}

export async function fetchExplain() {
  const body = document.getElementById("explain-body");
  const label = MODES[state.explain.mode];

  body.innerHTML = `<div class="explain-loading">LLM ${label} …</div><pre class="explain-result" id="explain-text" style="display:none"></pre>`;

  const textEl = document.getElementById("explain-text");

  state.explain.controller = new AbortController();

  try {
    const response = await fetch(
      `${API}/${state.explain.taskId}/explain?mode=${state.explain.mode}`,
      { signal: state.explain.controller.signal },
    );

    if (!response.ok) {
      const err = await response
        .json()
        .catch(() => ({ detail: response.statusText }));
      body.innerHTML = `<div class="explain-error">${esc(err.detail || "Request failed")}</div>`;
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let started = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        const token = line.slice(6);
        if (token === "[DONE]") break;

        if (!started) {
          document.querySelector(".explain-loading").style.display = "none";
          textEl.style.display = "";
          started = true;
        }

        textEl.textContent += token.replace(/\\n/g, "\n");
      }

      if (lines.some((l) => l === "data: [DONE]")) break;
    }
  } catch (err) {
    if (err.name === "AbortError") return;
    body.innerHTML = `<div class="explain-error">${esc(err.message)}</div>`;
  } finally {
    state.explain.controller = null;
  }
}
