"""HTML/CSS/JS helpers for the RazTodo web UI."""

from __future__ import annotations

APP_STYLES = """
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: system-ui, sans-serif;
  background: #0f0f0f;
  color: #e0e0e0;
  min-height: 100vh;
  padding: 2rem 1rem;
}
.container {
  max-width: 960px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 1.5rem;
}
.page-header h1 {
  margin: 0 0 0.4rem;
  color: #ab0000;
  font-size: 1.9rem;
}
.page-header p {
  margin: 0;
  color: #a5a5a5;
}
.panel {
  background: #171717;
  border: 1px solid #292929;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}
.panel h2 {
  margin: 0 0 0.85rem;
  font-size: 1rem;
  color: #f0f0f0;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.75rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field.full-width {
  grid-column: 1 / -1;
}
.field label {
  font-size: 0.82rem;
  color: #b5b5b5;
}
input, select, button {
  padding: 0.65rem 0.8rem;
  border-radius: 8px;
  border: 1px solid #333;
  background: #1d1d1d;
  color: #ededed;
  font-size: 0.95rem;
}
input:focus, select:focus {
  outline: 2px solid rgba(171, 0, 0, 0.35);
  border-color: #ab0000;
}
.actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}
button {
  background: #ab0000;
  border-color: #ab0000;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}
button:hover {
  background: #c00000;
}
button.secondary {
  background: #262626;
  border-color: #444;
  color: #d7d7d7;
}
button.secondary:hover {
  background: #313131;
}
button.danger,
.task-actions button.danger {
  color: #ff9d9d;
}
.search-row {
  display: flex;
  gap: 0.75rem;
}
.search-row input {
  flex: 1;
}
#status-msg {
  min-height: 1.25rem;
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: #95d6a4;
}
#status-msg.error {
  color: #ff8d8d;
}
.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.task-item {
  background: #171717;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.task-item.done .task-title {
  text-decoration: line-through;
  color: #8a8a8a;
}
.task-topline {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}
.task-title-block {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}
.task-title {
  margin: 0;
  font-size: 1rem;
  color: #f0f0f0;
  word-break: break-word;
}
.task-desc {
  margin: 0;
  color: #bbbbbb;
  font-size: 0.92rem;
  word-break: break-word;
}
.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}
.badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #262626;
  color: #bbbbbb;
}
.badge.priority-h { background: #4a0000; color: #ff8d8d; }
.badge.priority-m { background: #433100; color: #ffd37a; }
.badge.priority-l { background: #103010; color: #8be28b; }
.task-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.task-actions button {
  padding: 0.45rem 0.7rem;
  font-size: 0.82rem;
}
.empty-state {
  color: #7b7b7b;
  padding: 1rem;
  text-align: center;
  border: 1px dashed #333;
  border-radius: 12px;
}
@media (max-width: 640px) {
  body {
    padding: 1rem 0.75rem;
  }
  .task-topline {
    flex-direction: column;
  }
}
"""

APP_SCRIPT = """
const API = '/api/tasks';
let statusTimer = null;

function setStatus(message, isError = false) {
  const element = document.getElementById('status-msg');
  element.textContent = message;
  element.className = isError ? 'error' : '';

  if (statusTimer !== null) {
    clearTimeout(statusTimer);
  }

  if (message) {
    statusTimer = window.setTimeout(() => {
      element.textContent = '';
      element.className = '';
      statusTimer = null;
    }, 3000);
  }
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || response.statusText);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function esc(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderBadge(label, className = '') {
  return `<span class="badge ${className}">${esc(label)}</span>`;
}

function renderTask(task) {
  const description = task.description ? `<p class="task-desc">${esc(task.description)}</p>` : '';
  const badges = [
    task.priority ? renderBadge(`Priority ${task.priority}`, `priority-${task.priority.toLowerCase()}`) : '',
    task.due_date ? renderBadge(`Due ${task.due_date}`) : '',
    task.project ? renderBadge(`Project ${task.project}`) : '',
    task.tags && task.tags.length ? renderBadge(`Tags ${task.tags.join(', ')}`) : '',
  ].filter(Boolean).join('');

  return `
    <li class="task-item${task.done ? ' done' : ''}" id="task-${task.id}">
      <div class="task-topline">
        <div class="task-title-block">
          <h3 class="task-title">${esc(task.title)}</h3>
          ${description}
        </div>
        <div class="task-actions">
          <button type="button" onclick="toggleDone(${task.id}, ${task.done})">${task.done ? 'Undo' : 'Mark done'}</button>
          <button type="button" class="secondary danger" onclick="deleteTask(${task.id})">Delete</button>
        </div>
      </div>
      <div class="task-meta">${badges}</div>
    </li>`;
}

function renderTasks(tasks) {
  const taskList = document.getElementById('task-list');
  if (!tasks.length) {
    taskList.innerHTML = '<li class="empty-state">No tasks found.</li>';
    return;
  }
  taskList.innerHTML = tasks.map(renderTask).join('');
}

function getCreatePayload() {
  return {
    title: document.getElementById('new-title').value.trim(),
    description: document.getElementById('new-desc').value.trim(),
    priority: document.getElementById('new-priority').value || null,
    due_date: document.getElementById('new-due').value || null,
    tags: document.getElementById('new-tags').value
      .split(',')
      .map(tag => tag.trim())
      .filter(Boolean),
    project: document.getElementById('new-project').value.trim() || null,
  };
}

function resetCreateForm() {
  ['new-title', 'new-desc', 'new-due', 'new-tags', 'new-project'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('new-priority').value = '';
}

async function loadTasks() {
  const query = document.getElementById('search-input').value.trim();
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
    setStatus('Title is required.', true);
    return;
  }

  try {
    await api(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    resetCreateForm();
    setStatus('Task added.');
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function toggleDone(id, currentDone) {
  try {
    await api(`${API}/${id}/done`, { method: 'PATCH' });
    setStatus(currentDone ? 'Task marked as pending.' : 'Task marked as done.');
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteTask(id) {
  if (!confirm('Delete this task?')) {
    return;
  }

  try {
    await api(`${API}/${id}`, { method: 'DELETE' });
    setStatus('Task deleted.');
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function clearTasks() {
  if (!confirm('Delete all tasks? This cannot be undone.')) {
    return;
  }

  try {
    await api(`${API}/clear`, { method: 'POST' });
    setStatus('All tasks cleared.');
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function exportTasks() {
  try {
    const response = await fetch(`${API}/export`);
    if (!response.ok) {
      throw new Error('Export failed.');
    }
    const blob = await response.blob();
    const link = document.createElement('a');
    const objectUrl = URL.createObjectURL(blob);
    link.href = objectUrl;
    link.download = 'raztodo_export.json';
    link.click();
    URL.revokeObjectURL(objectUrl);
    setStatus('Tasks exported.');
  } catch (error) {
    setStatus(error.message, true);
  }
}

function openImportPicker() {
  document.getElementById('import-file').click();
}

async function importTasks(input) {
  const file = input.files[0];
  if (!file) {
    return;
  }

  try {
    const content = await file.text();
    const result = await api(`${API}/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: content,
    });
    setStatus(`Imported ${result.inserted} new and ${result.updated} updated task(s).`);
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    input.value = '';
  }
}

loadTasks();
"""


def _render_header() -> str:
    return """
    <header class="page-header">
      <h1>RazTodo</h1>
      <p>Manage your local tasks from a lightweight web interface.</p>
    </header>
    """


def _render_create_panel() -> str:
    return """
    <section class="panel" aria-labelledby="create-task-heading">
      <h2 id="create-task-heading">Create task</h2>
      <div class="form-grid">
        <div class="field full-width">
          <label for="new-title">Title</label>
          <input id="new-title" type="text" placeholder="Task title (required)" />
        </div>
        <div class="field full-width">
          <label for="new-desc">Description</label>
          <input id="new-desc" type="text" placeholder="Optional description" />
        </div>
        <div class="field">
          <label for="new-priority">Priority</label>
          <select id="new-priority">
            <option value="">None</option>
            <option value="H">High</option>
            <option value="M">Medium</option>
            <option value="L">Low</option>
          </select>
        </div>
        <div class="field">
          <label for="new-due">Due date</label>
          <input id="new-due" type="date" />
        </div>
        <div class="field">
          <label for="new-tags">Tags</label>
          <input id="new-tags" type="text" placeholder="work, urgent" />
        </div>
        <div class="field">
          <label for="new-project">Project</label>
          <input id="new-project" type="text" placeholder="Project name" />
        </div>
      </div>
      <div class="actions-row" style="margin-top: 1rem;">
        <button type="button" onclick="addTask()">Add task</button>
      </div>
    </section>
    """


def _render_search_panel() -> str:
    return """
    <section class="panel" aria-labelledby="search-heading">
      <h2 id="search-heading">Search</h2>
      <div class="search-row">
        <input id="search-input" type="text" placeholder="Search titles and descriptions" oninput="loadTasks()" />
      </div>
    </section>
    """


def _render_tools_panel() -> str:
    return """
    <section class="panel" aria-labelledby="tools-heading">
      <h2 id="tools-heading">Tools</h2>
      <div class="actions-row">
        <button type="button" class="secondary" onclick="exportTasks()">Export JSON</button>
        <button type="button" class="secondary" onclick="openImportPicker()">Import JSON</button>
        <button type="button" class="secondary danger" onclick="clearTasks()">Clear all</button>
        <input id="import-file" type="file" accept=".json,application/json" style="display: none" onchange="importTasks(this)" />
      </div>
    </section>
    """


def _render_task_panel() -> str:
    return """
    <section class="panel" aria-labelledby="task-list-heading">
      <h2 id="task-list-heading">Tasks</h2>
      <div id="status-msg" aria-live="polite"></div>
      <ul id="task-list" class="task-list"></ul>
    </section>
    """


def render_index_html() -> str:
    """Render the single-page web UI."""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        "  <title>RazTodo</title>\n"
        "  <style>\n" + APP_STYLES + "\n  </style>\n"
        "</head>\n"
        "<body>\n"
        '  <main class="container">\n'
        + _render_header()
        + _render_create_panel()
        + _render_search_panel()
        + _render_tools_panel()
        + _render_task_panel()
        + "  </main>\n"
        "  <script>\n" + APP_SCRIPT + "\n  </script>\n"
        "</body>\n"
        "</html>"
    )
