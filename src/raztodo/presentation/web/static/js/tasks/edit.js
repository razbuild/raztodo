import { API, api } from "../shared/api.js";
import { state } from "../shared/state.js";
import { setStatus } from "../shared/toast.js";
import { renderTasks } from "./render.js";
import { loadTasks } from "./actions.js";

export function startEdit(id) {
  state.editingTaskId = id;
  renderTasks(state.tasks);
  requestAnimationFrame(() => {
    const el = document.getElementById(`edit-title-${id}`);
    if (el) {
      el.focus();
      el.select();
    }
  });
}

export function cancelEdit() {
  state.editingTaskId = null;
  renderTasks(state.tasks);
}

export async function saveEdit(id) {
  const payload = {
    title: document.getElementById(`edit-title-${id}`).value.trim(),
    description: document.getElementById(`edit-desc-${id}`).value.trim(),
    priority: document.getElementById(`edit-priority-${id}`).value || null,
    due_date: document.getElementById(`edit-due-${id}`).value || null,
    tags: document
      .getElementById(`edit-tags-${id}`)
      .value.split(",")
      .map((t) => t.trim())
      .filter(Boolean),
    project: document.getElementById(`edit-project-${id}`).value.trim() || null,
  };

  if (!payload.title) {
    setStatus("Title is required.", true);
    return;
  }

  try {
    await api(`${API}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.editingTaskId = null;
    setStatus("Task updated.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}
