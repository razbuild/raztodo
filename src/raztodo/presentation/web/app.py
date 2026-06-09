"""FastAPI application for RazTodo web UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from raztodo.presentation.web.routes.tasks import router as tasks_router

app = FastAPI(
    title="RazTodo",
    description="Local web interface for RazTodo",
    version="0.4.1",
)

app.include_router(tasks_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> str:
    """Serve the single-page UI."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RazTodo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, sans-serif;
      background: #0f0f0f;
      color: #e0e0e0;
      min-height: 100vh;
      padding: 2rem 1rem;
    }
    h1 { color: #ab0000; margin-bottom: 1.5rem; font-size: 1.8rem; }
    .container { max-width: 800px; margin: 0 auto; }

    /* Form */
    .form-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }
    input, select, button {
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
      border: 1px solid #333;
      background: #1b1b1b;
      color: #e0e0e0;
      font-size: 0.9rem;
    }
    input[type="text"], input[type="date"] { flex: 1; min-width: 140px; }
    button {
      background: #ab0000;
      border-color: #ab0000;
      color: #fff;
      cursor: pointer;
      font-weight: 600;
    }
    button:hover { background: #c00000; }
    button.secondary {
      background: #2a2a2a;
      border-color: #444;
      color: #ccc;
    }
    button.secondary:hover { background: #333; }

    /* Search */
    .search-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
    .search-row input { flex: 1; }

    /* Task list */
    #task-list { list-style: none; }
    .task-item {
      background: #1b1b1b;
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      padding: 0.75rem 1rem;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .task-item.done .task-title { text-decoration: line-through; color: #666; }
    .task-title { flex: 1; font-size: 0.95rem; }
    .badge {
      font-size: 0.75rem;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      background: #2a2a2a;
      color: #aaa;
    }
    .badge.H { background: #4a0000; color: #ff6b6b; }
    .badge.M { background: #3a2a00; color: #ffc56b; }
    .badge.L { background: #0a2a0a; color: #6bff6b; }
    .task-actions { display: flex; gap: 0.4rem; }
    .task-actions button { padding: 0.25rem 0.6rem; font-size: 0.8rem; }

    /* Toolbar */
    .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
    #status-msg {
      margin-bottom: 1rem;
      color: #6bff6b;
      font-size: 0.85rem;
      min-height: 1.2em;
    }
    #status-msg.error { color: #ff6b6b; }
  </style>
</head>
<body>
<div class="container">
  <h1>⚡ RazTodo</h1>

  <!-- Add task form -->
  <div class="form-row">
    <input id="new-title" type="text" placeholder="Task title (required)" />
    <input id="new-desc"  type="text" placeholder="Description" />
    <select id="new-priority">
      <option value="">Priority</option>
      <option value="H">High</option>
      <option value="M">Medium</option>
      <option value="L">Low</option>
    </select>
    <input id="new-due" type="date" />
    <input id="new-tags"    type="text" placeholder="Tags (comma-sep)" />
    <input id="new-project" type="text" placeholder="Project" />
    <button onclick="addTask()">+ Add</button>
  </div>

  <!-- Search -->
  <div class="search-row">
    <input id="search-input" type="text" placeholder="Search tasks…" oninput="loadTasks()" />
  </div>

  <!-- Toolbar -->
  <div class="toolbar">
    <button class="secondary" onclick="exportTasks()">⬇ Export JSON</button>
    <label>
      <button class="secondary" onclick="document.getElementById('import-file').click()">
        ⬆ Import JSON
      </button>
      <input id="import-file" type="file" accept=".json" style="display:none"
             onchange="importTasks(this)" />
    </label>
    <button class="secondary" onclick="clearTasks()" style="color:#ff6b6b">🗑 Clear all</button>
  </div>

  <div id="status-msg"></div>
  <ul id="task-list"></ul>
</div>

<script>
  const API = '/api/tasks';

  function setStatus(msg, isError = false) {
    const el = document.getElementById('status-msg');
    el.textContent = msg;
    el.className = isError ? 'error' : '';
    if (msg) setTimeout(() => { el.textContent = ''; el.className = ''; }, 3000);
  }

  async function api(path, opts = {}) {
    const res = await fetch(path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  async function loadTasks() {
    const q = document.getElementById('search-input').value.trim();
    const url = q ? `${API}?q=${encodeURIComponent(q)}` : API;
    try {
      const tasks = await api(url);
      renderTasks(tasks);
    } catch (e) { setStatus(e.message, true); }
  }

  function renderTasks(tasks) {
    const ul = document.getElementById('task-list');
    if (!tasks.length) { ul.innerHTML = '<li style="color:#555;padding:1rem">No tasks found.</li>'; return; }
    ul.innerHTML = tasks.map(t => `
      <li class="task-item${t.done ? ' done' : ''}" id="task-${t.id}">
        <span class="task-title">${esc(t.title)}</span>
        ${t.priority ? `<span class="badge ${t.priority}">${t.priority}</span>` : ''}
        ${t.due_date  ? `<span class="badge">📅 ${t.due_date}</span>` : ''}
        ${t.project   ? `<span class="badge">📁 ${esc(t.project)}</span>` : ''}
        <div class="task-actions">
          <button onclick="toggleDone(${t.id}, ${t.done})">${t.done ? '↩ Undo' : '✓ Done'}</button>
          <button onclick="deleteTask(${t.id})" style="color:#ff6b6b">✕</button>
        </div>
      </li>`).join('');
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  async function addTask() {
    const title = document.getElementById('new-title').value.trim();
    if (!title) { setStatus('Title is required', true); return; }
    try {
      await api(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          description: document.getElementById('new-desc').value.trim(),
          priority:    document.getElementById('new-priority').value || null,
          due_date:    document.getElementById('new-due').value || null,
          tags:        document.getElementById('new-tags').value.split(',').map(t=>t.trim()).filter(Boolean),
          project:     document.getElementById('new-project').value.trim() || null,
        }),
      });
      ['new-title','new-desc','new-due','new-tags','new-project'].forEach(id => {
        document.getElementById(id).value = '';
      });
      document.getElementById('new-priority').value = '';
      setStatus('Task added!');
      loadTasks();
    } catch (e) { setStatus(e.message, true); }
  }

  async function toggleDone(id, currentDone) {
    try {
      await api(`${API}/${id}/done`, { method: 'PATCH' });
      setStatus(currentDone ? 'Marked pending' : 'Marked done');
      loadTasks();
    } catch (e) { setStatus(e.message, true); }
  }

  async function deleteTask(id) {
    if (!confirm('Delete this task?')) return;
    try {
      await api(`${API}/${id}`, { method: 'DELETE' });
      setStatus('Task deleted');
      loadTasks();
    } catch (e) { setStatus(e.message, true); }
  }

  async function clearTasks() {
    if (!confirm('Delete ALL tasks? This cannot be undone.')) return;
    try {
      await api(`${API}/clear`, { method: 'POST' });
      setStatus('All tasks cleared');
      loadTasks();
    } catch (e) { setStatus(e.message, true); }
  }

  async function exportTasks() {
    try {
      const res = await fetch(`${API}/export`);
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'raztodo_export.json';
      a.click();
      setStatus('Exported!');
    } catch (e) { setStatus(e.message, true); }
  }

  async function importTasks(input) {
    const file = input.files[0];
    if (!file) return;
    const text = await file.text();
    try {
      const data = await api(`${API}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: text,
      });
      setStatus(`Imported: ${data.inserted} new, ${data.updated} updated`);
      loadTasks();
    } catch (e) { setStatus(e.message, true); }
    input.value = '';
  }

  loadTasks();
</script>
</body>
</html>"""
