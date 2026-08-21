import { initTheme } from "./shared/theme.js";
import { initPriorityPickers } from "./shared/priority.js";
import { initTasks } from "./tasks/index.js";
import { initExplain } from "./explain/index.js";

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initPriorityPickers();
  initTasks();
  initExplain();
});
