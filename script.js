const startButton = document.querySelector("#start-focus");
const focusSession = document.querySelector("#focus-session");
const sessionTimer = document.querySelector("#session-timer");
const pauseButton = document.querySelector("#pause-focus");
const endButton = document.querySelector("#end-focus");
const announcements = document.querySelector("#announcements");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const addTaskButton = document.querySelector("#add-task");
const addTaskForm = document.querySelector("#add-task-form");
const newTaskInput = document.querySelector("#new-task");
const notificationButton = document.querySelector(".icon-button");
const notificationDot = document.querySelector(".notification-dot");
const toastMessage = document.querySelector("#toast-message");

let remainingSeconds = 25 * 60;
let timerInterval = null;
let toastTimeout = null;
let isPaused = false;

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
  const remainder = (seconds % 60).toString().padStart(2, "0");
  return `${minutes}:${remainder}`;
}

function updateTimer() {
  sessionTimer.textContent = formatTime(remainingSeconds);
}

function updateTaskCount() {
  const rows = [...taskList.querySelectorAll(".task-row")];
  const completed = rows.filter((row) => row.querySelector("input").checked).length;
  taskCount.textContent = `${completed} de ${rows.length} feitos`;
}

function updateTaskRow(input) {
  const row = input.closest(".task-row");
  const tag = row.querySelector(".task-tag");
  row.classList.toggle("is-done", input.checked);
  tag.textContent = input.checked ? "Feito" : "Opcional";
  tag.classList.toggle("tag-done", input.checked);
  tag.classList.remove("tag-next");
  updateTaskCount();
}

function endSession(message) {
  window.clearInterval(timerInterval);
  timerInterval = null;
  remainingSeconds = 25 * 60;
  isPaused = false;
  updateTimer();
  focusSession.hidden = true;
  startButton.querySelector("span").textContent = "Começar sessão";
  pauseButton.textContent = "Pausar";
  announcements.textContent = message;
  startButton.focus();
}

function finishSession() {
  const focusTask = taskList.querySelector("[data-focus-task]");
  if (focusTask && !focusTask.checked) {
    focusTask.checked = true;
    updateTaskRow(focusTask);
  }
  endSession("Sessão concluída. A tarefa foi marcada como feita.");
}

function startTimer() {
  timerInterval = window.setInterval(() => {
    remainingSeconds -= 1;
    updateTimer();

    if (remainingSeconds <= 0) {
      finishSession();
    }
  }, 1000);
}

startButton.addEventListener("click", () => {
  focusSession.hidden = false;
  startButton.querySelector("span").textContent = "Sessão em andamento";
  announcements.textContent = "Sessão de foco iniciada. O cronômetro está contando 25 minutos.";
  startTimer();
  pauseButton.focus();
});

pauseButton.addEventListener("click", () => {
  isPaused = !isPaused;
  pauseButton.textContent = isPaused ? "Retomar" : "Pausar";

  if (isPaused) {
    window.clearInterval(timerInterval);
    timerInterval = null;
    announcements.textContent = "Sessão pausada.";
  } else {
    startTimer();
    announcements.textContent = "Sessão retomada.";
  }
});

endButton.addEventListener("click", () => {
  endSession("Sessão encerrada. Seu plano continua disponível para quando quiser voltar.");
});

taskList.addEventListener("change", (event) => {
  if (event.target instanceof HTMLInputElement && event.target.type === "checkbox") {
    updateTaskRow(event.target);
    announcements.textContent = `${taskCount.textContent.replace(" feitos", " tarefas feitas")}.`;
  }
});

addTaskButton.addEventListener("click", () => {
  addTaskForm.hidden = false;
  addTaskButton.setAttribute("aria-expanded", "true");
  newTaskInput.focus();
});

newTaskInput.addEventListener("input", () => {
  newTaskInput.setCustomValidity("");
});

addTaskForm.addEventListener("submit", (event) => {
  event.preventDefault();
  newTaskInput.value = newTaskInput.value.trim();

  if (!newTaskInput.value) {
    newTaskInput.setCustomValidity("Escreva o nome da tarefa.");
    newTaskInput.reportValidity();
    return;
  }

  const row = taskList.lastElementChild.cloneNode(true);
  const checkbox = row.querySelector("input");
  const title = row.querySelector(".task-copy strong");
  const metadata = row.querySelector(".task-copy small");
  const tag = row.querySelector(".task-tag");

  checkbox.checked = false;
  checkbox.removeAttribute("data-focus-task");
  title.textContent = newTaskInput.value;
  metadata.innerHTML = "";
  const separator = document.createElement("span");
  separator.textContent = "·";
  separator.setAttribute("aria-hidden", "true");
  metadata.append("Seu plano ", separator, " livre");
  tag.textContent = "Opcional";
  tag.classList.remove("tag-done", "tag-next");
  row.classList.remove("is-done");
  taskList.append(row);
  addTaskForm.reset();
  addTaskForm.hidden = true;
  addTaskButton.setAttribute("aria-expanded", "false");
  addTaskButton.focus();
  updateTaskCount();
  announcements.textContent = `Tarefa adicionada: ${title.textContent}.`;
});

notificationButton.addEventListener("click", () => {
  const message = "Você está em dia com seu plano. Nenhuma novidade por aqui.";
  notificationDot.hidden = true;
  notificationButton.setAttribute("aria-label", "Notificações. Nenhuma novidade.");
  toastMessage.textContent = message;
  toastMessage.hidden = false;
  announcements.textContent = message;
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => {
    toastMessage.hidden = true;
  }, 3200);
});

updateTaskCount();
