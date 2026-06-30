const API = "/api/tasks";
let toastTimer = null;
let editingTaskId = null;
let lastTasks = [];
let currentFilter = "all";

function setStatus(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = isError ? "error" : "";

  if (toastTimer !== null) {
    clearTimeout(toastTimer);
    toast.classList.remove("show");
  }

  if (!message) return;

  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add("show"));
  });

  toastTimer = window.setTimeout(() => {
    toast.classList.remove("show");
    toastTimer = null;
  }, 3000);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const payload = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || response.statusText);
  }
  if (response.status === 204) return null;
  return response.json();
}

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderBadge(label, className = "") {
  return `<span class="badge ${className}">${esc(label)}</span>`;
}

function renderTask(task) {
  if (editingTaskId === task.id) {
    return `
<li class="task-item" id="task-${task.id}">
    <div class="edit-form">
        <input id="edit-title-${task.id}" type="text" value="${esc(task.title)}" placeholder="Title" class="input-primary" onkeydown="if(event.key==='Enter') saveEdit(${task.id})" />
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
            <button type="button" class="btn-save"   onclick="saveEdit(${task.id})">Save</button>
            <button type="button" class="btn-cancel" onclick="cancelEdit()">Cancel</button>
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
            <button type="button" class="btn-done" onclick="toggleDone(${task.id}, ${task.done})">
                ${doneLabel}
            </button>

            <button
                type="button"
                class="btn-explain"
                onclick="openExplain(${task.id})">
                Explain
            </button>

            <button type="button" class="btn-edit" onclick="startEdit(${task.id})">
                Edit
            </button>

            <button type="button" class="btn-delete" onclick="deleteTask(${task.id})">
                Delete
            </button>
        </div>
    </div>
    ${badges ? `<div class="task-meta">${badges}</div>` : ""}
</li>`;
}

function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll(".filter-tab").forEach((btn) => {
    const active = btn.dataset.filter === filter;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", active);
  });
  renderTasks(lastTasks);
}

function renderTasks(tasks) {
  lastTasks = tasks;
  const filtered =
    currentFilter === "pending"
      ? tasks.filter((t) => !t.done)
      : currentFilter === "done"
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
    ${currentFilter === "done" ? "No completed tasks yet." : currentFilter === "pending" ? "No pending tasks — all done!" : "No tasks yet. Add one to get started."}
</li>`;
    return;
  }

  taskList.innerHTML = filtered.map(renderTask).join("");
}

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

async function loadTasks() {
  const query = document.getElementById("search-input").value.trim();
  const url = query ? `${API}?q=${encodeURIComponent(query)}` : API;
  try {
    renderTasks(await api(url));
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function addTask() {
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

document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("new-title");
  if (titleInput) {
    titleInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") addTask();
    });
  }
});

async function toggleDone(id, currentDone) {
  try {
    await api(`${API}/${id}/done`, { method: "PATCH" });
    setStatus(currentDone ? "Marked as pending." : "Marked as done.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  try {
    await api(`${API}/${id}`, { method: "DELETE" });
    setStatus("Task deleted.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function clearTasks() {
  if (!confirm("Delete all tasks? This cannot be undone.")) return;
  try {
    await api(`${API}/clear`, { method: "POST" });
    setStatus("All tasks cleared.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function exportTasks() {
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

function openImportPicker() {
  document.getElementById("import-file").click();
}

async function importTasks(input) {
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

function startEdit(id) {
  editingTaskId = id;
  renderTasks(lastTasks);
  requestAnimationFrame(() => {
    const el = document.getElementById(`edit-title-${id}`);
    if (el) {
      el.focus();
      el.select();
    }
  });
}

function cancelEdit() {
  editingTaskId = null;
  renderTasks(lastTasks);
}

async function saveEdit(id) {
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
    editingTaskId = null;
    setStatus("Task updated.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

loadTasks();

// ── Explain modal ────────────────────────────────────

let explainCurrentId = null;
let explainCurrentMode = "short";
let explainController = null;

const MODES = {
  short: "Summary",
  deep: "Deep Analysis",
  plan: "Action Plan",
};

function openExplain(taskId) {
  const task = lastTasks.find((t) => t.id === taskId);
  explainCurrentId = taskId;
  explainCurrentMode = "short";

  document.getElementById("modal-title").textContent = task
    ? task.title
    : `Task #${taskId}`;

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === "short");
  });

  document.getElementById("explain-backdrop").classList.add("open");
  _fetchExplain();
}

function closeExplain() {
  if (explainController) {
    explainController.abort();
    explainController = null;
  }
  document.getElementById("explain-backdrop").classList.remove("open");
  explainCurrentId = null;
}

function switchMode(mode) {
  if (mode === explainCurrentMode) return;
  if (explainController) {
    explainController.abort();
    explainController = null;
  }
  explainCurrentMode = mode;
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
  _fetchExplain();
}

async function _fetchExplain() {
  const body = document.getElementById("explain-body");
  const label = MODES[explainCurrentMode];

  body.innerHTML = `<div class="explain-loading">LLM ${label} …</div><pre class="explain-result" id="explain-text" style="display:none"></pre>`;

  const textEl = document.getElementById("explain-text");

  explainController = new AbortController();

  try {
    const response = await fetch(
      `${API}/${explainCurrentId}/explain?mode=${explainCurrentMode}`,
      { signal: explainController.signal },
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
    explainController = null;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("explain-backdrop").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) closeExplain();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeExplain();
  });
});
