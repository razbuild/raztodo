import {
  addTask,
  clearTasks,
  deleteTask,
  exportTasks,
  importTasks,
  loadTasks,
  openImportPicker,
  setFilter,
  toggleDone,
} from "./actions.js";
import { cancelEdit, saveEdit, startEdit } from "./edit.js";

function initCreateForm() {
  document.querySelector(".btn-primary")?.addEventListener("click", addTask);

  const titleInput = document.getElementById("new-title");
  if (titleInput) {
    titleInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") addTask();
    });
  }
}

function initSearch() {
  document.getElementById("search-input")?.addEventListener("input", loadTasks);
}

function initFilters() {
  document.querySelectorAll(".filter-tab[data-filter]").forEach((button) => {
    button.addEventListener("click", () => setFilter(button.dataset.filter));
  });
}

function initTools() {
  document.querySelector('.btn-ghost:not(.btn-danger-ghost)')?.addEventListener("click", exportTasks);
  document.querySelectorAll(".btn-ghost")[1]?.addEventListener("click", openImportPicker);
  document.querySelector(".btn-danger-ghost")?.addEventListener("click", clearTasks);
  document.getElementById("import-file")?.addEventListener("change", (e) => importTasks(e.target));
}

function initTaskListActions() {
  document.getElementById("task-list")?.addEventListener("click", (e) => {
    const button = e.target.closest("button[data-action]");
    if (!button) return;

    const id = Number(button.dataset.id);
    if (button.dataset.action === "toggle-done") toggleDone(id, button.dataset.done === "true");
    if (button.dataset.action === "open-explain") window.openExplain(id);
    if (button.dataset.action === "start-edit") startEdit(id);
    if (button.dataset.action === "delete-task") deleteTask(id);
    if (button.dataset.action === "save-edit") saveEdit(id);
    if (button.dataset.action === "cancel-edit") cancelEdit();
  });

  document.getElementById("task-list")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.target.matches("[data-edit-title]")) {
      saveEdit(Number(e.target.dataset.editTitle));
    }
  });
}

export function initTasks() {
  initCreateForm();
  initSearch();
  initFilters();
  initTools();
  initTaskListActions();
  loadTasks();
}
