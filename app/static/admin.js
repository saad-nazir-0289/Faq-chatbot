const statsCardsEl = document.getElementById("statsCards");
const leadsTableEl = document.getElementById("leadsTable");
const appointmentsTableEl = document.getElementById("appointmentsTable");
const refreshDashboardButtonEl = document.getElementById("refreshDashboardButton");
const seedDemoButtonEl = document.getElementById("seedDemoButton");
const historyFormEl = document.getElementById("historyForm");
const sessionLookupInputEl = document.getElementById("sessionLookupInput");
const conversationListEl = document.getElementById("conversationList");
const historyResultEl = document.getElementById("historyResult");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderStatCards(stats) {
  const entries = [
    ["FAQs", stats.faq_count],
    ["Conversations", stats.conversation_count],
    ["Leads", stats.lead_count],
    ["Consultations", stats.appointment_request_count],
  ];

  statsCardsEl.innerHTML = entries
    .map(
      ([label, value]) =>
        `<div class="stat-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`,
    )
    .join("");
}

function renderTable(target, rows, columns) {
  if (!rows.length) {
    target.innerHTML = '<p class="empty-state">No demo records yet. Use the chat page to create some.</p>';
    return;
  }

  const header = columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = columns
        .map((column) => `<td>${escapeHtml(row[column.key] ?? "-")}</td>`)
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  target.innerHTML = `<table class="admin-table"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
}

function renderHistory(payload) {
  if (!payload.messages.length) {
    historyResultEl.innerHTML = '<p class="empty-state">No conversation found for that session id.</p>';
    return;
  }

  historyResultEl.innerHTML = `
    <div class="history-meta">
      <span>Session: ${escapeHtml(payload.session_id)}</span>
      <span>State: ${escapeHtml(payload.current_state)}</span>
    </div>
    <div class="history-log">
      ${payload.messages
        .map(
          (message) => `
            <article class="history-message ${message.role === "user" ? "user-history" : "bot-history"}">
              <strong>${escapeHtml(message.role)}</strong>
              <p>${escapeHtml(message.content)}</p>
              <span>${escapeHtml(message.created_at)}</span>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderConversationList(conversations) {
  if (!conversations.length) {
    conversationListEl.innerHTML = '<p class="empty-state">No recent sessions yet.</p>';
    return;
  }

  conversationListEl.innerHTML = conversations
    .map(
      (conversation) => `
        <button class="conversation-chip" type="button" data-session-id="${escapeHtml(conversation.session_id)}">
          <strong>${escapeHtml(conversation.current_state)}</strong>
          <span>${escapeHtml(conversation.session_id)}</span>
          <small>${escapeHtml(conversation.message_count)} messages</small>
        </button>
      `,
    )
    .join("");

  conversationListEl.querySelectorAll("[data-session-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const sessionId = button.getAttribute("data-session-id");
      sessionLookupInputEl.value = sessionId;
      const payload = await fetchJson(`/admin/conversations/${encodeURIComponent(sessionId)}`);
      renderHistory(payload);
    });
  });
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Failed request: ${url}`);
  }
  return response.json();
}

async function loadDashboard() {
  const [stats, leads, appointments, conversations] = await Promise.all([
    fetchJson("/admin/stats"),
    fetchJson("/admin/leads"),
    fetchJson("/admin/appointments"),
    fetchJson("/admin/conversations"),
  ]);

  renderStatCards(stats);
  renderTable(leadsTableEl, leads, [
    { key: "name", label: "Name" },
    { key: "email", label: "Email" },
    { key: "phone", label: "Phone" },
    { key: "company", label: "Company" },
    { key: "need", label: "Need" },
  ]);
  renderTable(appointmentsTableEl, appointments, [
    { key: "name", label: "Name" },
    { key: "company", label: "Company" },
    { key: "preferred_date", label: "Date" },
    { key: "preferred_time", label: "Time" },
    { key: "status", label: "Status" },
  ]);
  renderConversationList(conversations);
}

historyFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const sessionId = sessionLookupInputEl.value.trim();
  if (!sessionId) {
    return;
  }

  try {
    const payload = await fetchJson(`/admin/conversations/${encodeURIComponent(sessionId)}`);
    renderHistory(payload);
  } catch (error) {
    historyResultEl.innerHTML = '<p class="empty-state">Unable to load conversation history right now.</p>';
  }
});

refreshDashboardButtonEl.addEventListener("click", async () => {
  await loadDashboard();
});

seedDemoButtonEl.addEventListener("click", async () => {
  seedDemoButtonEl.disabled = true;
  seedDemoButtonEl.textContent = "Seeding...";
  try {
    await fetchJson("/admin/demo/seed", { method: "POST" });
    await loadDashboard();
  } catch (error) {
    historyResultEl.innerHTML = '<p class="empty-state">Unable to seed demo data right now.</p>';
  } finally {
    seedDemoButtonEl.disabled = false;
    seedDemoButtonEl.textContent = "Seed sample data";
  }
});

loadDashboard().catch(() => {
  statsCardsEl.innerHTML = '<p class="empty-state">Unable to load dashboard data.</p>';
  leadsTableEl.innerHTML = '<p class="empty-state">Unable to load lead data.</p>';
  appointmentsTableEl.innerHTML = '<p class="empty-state">Unable to load consultation data.</p>';
  conversationListEl.innerHTML = '<p class="empty-state">Unable to load conversation data.</p>';
});
