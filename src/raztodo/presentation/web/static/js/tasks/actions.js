import { API, api } from "../shared/api.js";
import { state } from "../shared/state.js";
import { setStatus } from "../shared/toast.js";
import { renderTasks } from "./render.js";

function getCreatePayload() {
  return {
    title: document.getElementById("new-title").value.trim(),
    description: document.getElementById("new-desc").value.trim(),
    priority: document.getElementById("new-priority").value || null,
    due_date: document.getElementById("new-due").value || null,
    tags: document
      .getElementById("new-tags")
      .value.split(",")
      .map((t) => t.trim())
      .filter(Boolean),
    project: document.getElementById("new-project").value.trim() || null,
  };
}

function resetCreateForm() {
  ["new-title", "new-desc", "new-due", "new-tags", "new-project"].forEach(
    (id) => {
      document.getElementById(id).value = "";
    },
  );
  document.getElementById("new-priority").value = "";
}

export async function loadTasks() {
  const query = document.getElementById("search-input").value.trim();
  const url = query ? `${API}?q=${encodeURIComponent(query)}` : API;
  try {
    renderTasks(await api(url));
  } catch (error) {
    setStatus(error.message, true);
  }
}

export async function addTask() {
  const payload = getCreatePayload();
  if (!payload.title) {
    setStatus("Title is required.", true);
    return;
  }
  try {
    await api(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    resetCreateForm();
    document.getElementById("new-title").focus();
    setStatus("Task added.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

export async function toggleDone(id, currentDone) {
  try {
    await api(`${API}/${id}/done`, { method: "PATCH" });
    setStatus(currentDone ? "Marked as pending." : "Marked as done.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

export async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  try {
    await api(`${API}/${id}`, { method: "DELETE" });
    setStatus("Task deleted.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

export async function clearTasks() {
  if (!confirm("Delete all tasks? This cannot be undone.")) return;
  try {
    await api(`${API}/clear`, { method: "POST" });
    setStatus("All tasks cleared.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

export async function exportTasks() {
  try {
    const response = await fetch(`${API}/export`);
    if (!response.ok) throw new Error("Export failed.");
    const blob = await response.blob();
    const link = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    link.href = objectUrl;
    link.download = "raztodo_export.json";
    link.click();
    URL.revokeObjectURL(objectUrl);
    setStatus("Exported.");
  } catch (error) {
    setStatus(error.message, true);
  }
}

export function openImportPicker() {
  document.getElementById("import-file").click();
}

export async function importTasks(input) {
  const file = input.files[0];
  if (!file) return;
  try {
    const content = await file.text();
    const result = await api(`${API}/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: content,
    });
    setStatus(`Imported ${result.inserted} new, ${result.updated} updated.`);
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    input.value = "";
  }
}

export function setFilter(filter) {
  state.currentFilter = filter;
  document.querySelectorAll(".filter-tab").forEach((btn) => {
    const active = btn.dataset.filter === filter;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", active);
  });
  renderTasks(state.tasks);
}
