import { state } from "../shared/state.js";

export function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function renderBadge(label, className = "") {
  return `<span class="badge ${className}">${esc(label)}</span>`;
}

export function renderTask(task) {
  if (state.editingTaskId === task.id) {
    return `
<li class="task-item" id="task-${task.id}">
    <div class="edit-form">
        <input id="edit-title-${task.id}" type="text" value="${esc(task.title)}" placeholder="Title" class="input-primary" data-edit-title="${task.id}" />
        <input id="edit-desc-${task.id}"  type="text" value="${esc(task.description || "")}" placeholder="Description" />
        <div class="form-row">
            <div class="field">
                <label>Priority</label>
                <select id="edit-priority-${task.id}">
                    <option value=""  ${!task.priority ? "selected" : ""}>None</option>
                    <option value="H" ${task.priority === "H" ? "selected" : ""}>High</option>
                    <option value="M" ${task.priority === "M" ? "selected" : ""}>Medium</option>
                    <option value="L" ${task.priority === "L" ? "selected" : ""}>Low</option>
                </select>
            </div>
            <div class="field">
                <label>Due date</label>
                <input id="edit-due-${task.id}" type="date" value="${task.due_date || ""}" />
            </div>
            <div class="field">
                <label>Tags</label>
                <input id="edit-tags-${task.id}" type="text" value="${esc((task.tags || []).join(", "))}" />
            </div>
            <div class="field">
                <label>Project</label>
                <input id="edit-project-${task.id}" type="text" value="${esc(task.project || "")}" />
            </div>
        </div>
        <div class="edit-actions">
            <button type="button" class="btn-save"   data-action="save-edit" data-id="${task.id}">Save</button>
            <button type="button" class="btn-cancel" data-action="cancel-edit">Cancel</button>
        </div>
    </div>
</li>`;
  }

  const description = task.description
    ? `<p class="task-desc">${esc(task.description)}</p>`
    : "";

  const today = new Date().toISOString().slice(0, 10);
  const isOverdue = task.due_date && !task.done && task.due_date < today;

  const badges = [
    task.priority
      ? renderBadge(
          `${task.priority === "H" ? "High" : task.priority === "M" ? "Medium" : "Low"} priority`,
          `priority-${task.priority.toLowerCase()}`,
        )
      : "",
    isOverdue
      ? renderBadge("Overdue", "overdue")
      : task.due_date
        ? renderBadge(`Due ${task.due_date}`)
        : "",
    task.project ? renderBadge(task.project, "project") : "",
    task.tags && task.tags.length
      ? renderBadge(task.tags.join(", "), "tag")
      : "",
  ]
    .filter(Boolean)
    .join("");

  const doneLabel = task.done ? "Undo" : "Done";

  return `
<li class="task-item${task.done ? " done" : ""}" id="task-${task.id}">
    <div class="task-topline">
        <div class="task-title-block">
            <h3 class="task-title">${esc(task.title)}</h3>
            ${description}
        </div>
        <div class="task-actions">
            <button type="button" class="btn-done" data-action="toggle-done" data-id="${task.id}" data-done="${task.done}">
                ${doneLabel}
            </button>

            <button
                type="button"
                class="btn-explain"
                data-action="open-explain" data-id="${task.id}">
                Explain
            </button>

            <button type="button" class="btn-edit" data-action="start-edit" data-id="${task.id}">
                Edit
            </button>

            <button type="button" class="btn-delete" data-action="delete-task" data-id="${task.id}">
                Delete
            </button>
        </div>
    </div>
    ${badges ? `<div class="task-meta">${badges}</div>` : ""}
</li>`;
}

export function renderTasks(tasks) {
  state.tasks = tasks;
  const filtered =
    state.currentFilter === "pending"
      ? tasks.filter((t) => !t.done)
      : state.currentFilter === "done"
        ? tasks.filter((t) => t.done)
        : tasks;
  const taskList = document.getElementById("task-list");
  const countEl = document.getElementById("task-count");

  if (countEl) {
    const pending = tasks.filter((t) => !t.done).length;
    countEl.textContent = tasks.length
      ? `${pending} pending · ${tasks.length} total`
      : "";
  }

  if (!filtered.length) {
    taskList.innerHTML = `
<li class="empty-state">
    <span class="empty-state-icon">✓</span>
    ${state.currentFilter === "done" ? "No completed tasks yet." : state.currentFilter === "pending" ? "No pending tasks — all done!" : "No tasks yet. Add one to get started."}
</li>`;
    return;
  }

  taskList.innerHTML = filtered.map(renderTask).join("");
}
