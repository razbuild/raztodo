const API = "/api/tasks";
let statusTimer = null;

function setStatus(message, isError = false) {
  const element = document.getElementById("status-msg");
  element.textContent = message;
  element.className = isError ? "error" : "";

  if (statusTimer !== null) {
    clearTimeout(statusTimer);
  }

  if (message) {
    statusTimer = window.setTimeout(() => {
      element.textContent = "";
      element.className = "";
      statusTimer = null;
    }, 3000);
  }
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const payload = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || response.statusText);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderBadge(label, className = "") {
  return `<span class="badge ${className}">${esc(label)}</span>`;
}

function renderTask(task) {
  const description = task.description
    ? `<p class="task-desc">${esc(task.description)}</p>`
    : "";
  const badges = [
    task.priority
      ? renderBadge(
          `Priority ${task.priority}`,
          `priority-${task.priority.toLowerCase()}`,
        )
      : "",
    task.due_date ? renderBadge(`Due ${task.due_date}`) : "",
    task.project ? renderBadge(`Project ${task.project}`) : "",
    task.tags && task.tags.length
      ? renderBadge(`Tags ${task.tags.join(", ")}`)
      : "",
  ]
    .filter(Boolean)
    .join("");

  return `
    <li class="task-item${task.done ? " done" : ""}" id="task-${task.id}">
      <div class="task-topline">
        <div class="task-title-block">
          <h3 class="task-title">${esc(task.title)}</h3>
          ${description}
        </div>
        <div class="task-actions">
          <button type="button" onclick="toggleDone(${task.id}, ${task.done})">${task.done ? "Undo" : "Mark done"}</button>
          <button type="button" class="secondary danger" onclick="deleteTask(${task.id})">Delete</button>
        </div>
      </div>
      <div class="task-meta">${badges}</div>
    </li>`;
}

function renderTasks(tasks) {
  const taskList = document.getElementById("task-list");
  if (!tasks.length) {
    taskList.innerHTML = '<li class="empty-state">No tasks found.</li>';
    return;
  }
  taskList.innerHTML = tasks.map(renderTask).join("");
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
      .map((tag) => tag.trim())
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
    setStatus("Task added.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function toggleDone(id, currentDone) {
  try {
    await api(`${API}/${id}/done`, { method: "PATCH" });
    setStatus(currentDone ? "Task marked as pending." : "Task marked as done.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteTask(id) {
  if (!confirm("Delete this task?")) {
    return;
  }

  try {
    await api(`${API}/${id}`, { method: "DELETE" });
    setStatus("Task deleted.");
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function clearTasks() {
  if (!confirm("Delete all tasks? This cannot be undone.")) {
    return;
  }

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
    if (!response.ok) {
      throw new Error("Export failed.");
    }
    const blob = await response.blob();
    const link = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    link.href = objectUrl;
    link.download = "raztodo_export.json";
    link.click();
    URL.revokeObjectURL(objectUrl);
    setStatus("Tasks exported.");
  } catch (error) {
    setStatus(error.message, true);
  }
}

function openImportPicker() {
  document.getElementById("import-file").click();
}

async function importTasks(input) {
  const file = input.files[0];
  if (!file) {
    return;
  }

  try {
    const content = await file.text();
    const result = await api(`${API}/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: content,
    });
    setStatus(
      `Imported ${result.inserted} new and ${result.updated} updated task(s).`,
    );
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    input.value = "";
  }
}

loadTasks();
