const messagesEl = document.getElementById("messages");
const quickRepliesEl = document.getElementById("quickReplies");
const formEl = document.getElementById("chatForm");
const inputEl = document.getElementById("messageInput");
const template = document.getElementById("messageTemplate");
const resetButtonEl = document.getElementById("resetChatButton");

let sessionId = window.localStorage.getItem("support-chat-session") || "";

function renderMessage(text, role) {
  const node = template.content.firstElementChild.cloneNode(true);
  node.classList.add(role === "user" ? "user" : "bot");
  node.querySelector(".message").textContent = text;
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderQuickReplies(replies) {
  quickRepliesEl.innerHTML = "";
  (replies || []).forEach((reply) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = reply;
    button.addEventListener("click", () => sendMessage(reply));
    quickRepliesEl.appendChild(button);
  });
}

async function startChat() {
  messagesEl.innerHTML = "";
  const response = await fetch("/chat/start", { method: "POST" });
  const payload = await response.json();
  sessionId = payload.session_id;
  window.localStorage.setItem("support-chat-session", sessionId);
  renderMessage(payload.message, "bot");
  renderQuickReplies(payload.quick_replies);
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message) {
    return;
  }

  if (!sessionId) {
    await startChat();
  }

  renderMessage(message, "user");
  inputEl.value = "";

  const response = await fetch("/chat/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (response.status === 404) {
    sessionId = "";
    window.localStorage.removeItem("support-chat-session");
    renderMessage("Your demo session expired, so I started a new one.", "bot");
    await startChat();
    await sendMessage(message);
    return;
  }

  if (!response.ok) {
    renderMessage("Sorry, something went wrong. Please refresh and try again.", "bot");
    return;
  }

  const payload = await response.json();
  renderMessage(payload.message, "bot");
  renderQuickReplies(payload.quick_replies);
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendMessage(inputEl.value);
});

startChat();

resetButtonEl.addEventListener("click", async () => {
  sessionId = "";
  window.localStorage.removeItem("support-chat-session");
  renderQuickReplies([]);
  await startChat();
});
