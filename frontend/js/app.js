/**
 * Main application shell for AI-901 Study Studio.
 */

import { api } from "./api.js";
import { studyState } from "./state.js";
import { copyToClipboard, escapeHtml } from "./utils.js";
import { renderGuidesView } from "./views/domains.js";
import { renderFlashcardsView } from "./views/flashcards.js";
import { renderExamView } from "./views/exam.js";
import { renderSandboxView } from "./views/sandbox.js";

let curriculum = null;
let statusInfo = null;
let currentView = "guides";

const views = {
  guides: document.getElementById("view-guides"),
  flashcards: document.getElementById("view-flashcards"),
  exam: document.getElementById("view-exam"),
  sandbox: document.getElementById("view-sandbox"),
};

function navigate(viewName) {
  if (!views[viewName]) return;
  currentView = viewName;

  Object.entries(views).forEach(([key, section]) => {
    section.classList.toggle("is-hidden", key !== viewName);
  });

  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.view === viewName);
  });

  window.scrollTo({ top: 0, behavior: "instant" });
}

function updateReadiness() {
  const pct = studyState.computeReadiness(curriculum);
  const el = document.getElementById("readiness-percent");
  if (el) el.textContent = `${pct}%`;
}

function updateModePill(status) {
  statusInfo = status;
  const dot = document.getElementById("mode-dot");
  const label = document.getElementById("mode-label");
  if (!dot || !label) return;

  dot.classList.remove("is-live", "is-hybrid");
  if (status.overall_mode === "live") {
    dot.classList.add("is-live");
    label.textContent = "Live Foundry";
  } else if (status.overall_mode === "hybrid") {
    dot.classList.add("is-hybrid");
    label.textContent = "Hybrid Mode";
  } else {
    label.textContent = "Demo Mode";
  }
}

function renderStatusModal() {
  const body = document.getElementById("status-modal-body");
  if (!body || !statusInfo) return;

  const rows = Object.values(statusInfo.services)
    .map(
      (svc) => `
        <div class="service-status-row">
          <div>
            <strong style="font-size:0.88rem;">${escapeHtml(svc.label)}</strong>
            <div class="service-env-list">${svc.env_vars.join(" · ")}</div>
          </div>
          <div style="display:flex; gap:0.4rem; align-items:center; flex-shrink:0;">
            <span class="badge ${svc.mode === "live" ? "badge-success" : "badge-warn"}">
              ${svc.mode === "live" ? "LIVE" : "DEMO"}
            </span>
          </div>
        </div>
      `
    )
    .join("");

  const envSnippet = `# Copy .env.example to .env and populate any service you want in Live Mode
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini`;

  body.innerHTML = `
    <div style="display:flex; align-items:center; justify-content:space-between; gap:0.5rem;">
      <span class="eyebrow">Overall Status: ${escapeHtml(statusInfo.overall_mode.toUpperCase())}</span>
      <span class="badge badge-neutral">AI901_MODE=${escapeHtml(statusInfo.configured_mode_flag)}</span>
    </div>
    ${rows}
    <div class="code-panel">
      <div class="code-panel-head">
        <span>Quick-start .env for Live Microsoft Foundry</span>
        <button class="btn btn-subtle btn-sm" id="copy-env-snippet" type="button">Copy .env</button>
      </div>
      <pre><code>${escapeHtml(envSnippet)}</code></pre>
    </div>
  `;

  body.querySelector("#copy-env-snippet").addEventListener("click", () => {
    copyToClipboard(envSnippet, ".env template copied!");
  });
}

function setupHeaderAndModal() {
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.addEventListener("click", () => navigate(tab.dataset.view));
  });

  const brand = document.getElementById("brand-home");
  if (brand) {
    brand.addEventListener("click", () => navigate("guides"));
    brand.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        navigate("guides");
      }
    });
  }

  const modal = document.getElementById("status-modal");
  const openBtn = document.getElementById("mode-status-btn");
  const closeBtn = document.getElementById("close-status-modal");
  const doneBtn = document.getElementById("done-status-modal");
  const refreshBtn = document.getElementById("refresh-status-btn");

  const closeModal = () => modal.classList.add("is-hidden");
  openBtn.addEventListener("click", () => {
    renderStatusModal();
    modal.classList.remove("is-hidden");
  });
  closeBtn.addEventListener("click", closeModal);
  doneBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  refreshBtn.addEventListener("click", async () => {
    const fresh = await api.getStatus();
    updateModePill(fresh);
    renderStatusModal();
  });
}

async function init() {
  setupHeaderAndModal();
  const loading = document.getElementById("loading-state");

  try {
    const [currData, statusData] = await Promise.all([
      api.getCurriculum(),
      api.getStatus(),
    ]);
    curriculum = currData;
    updateModePill(statusData);
    updateReadiness();
    studyState.subscribe(updateReadiness);

    renderGuidesView(views.guides, curriculum, { onNavigate: navigate });
    renderFlashcardsView(views.flashcards, curriculum);
    renderExamView(views.exam, curriculum);
    renderSandboxView(views.sandbox, curriculum);

    loading.classList.add("is-hidden");
    navigate(currentView);
  } catch (err) {
    loading.innerHTML = `
      <div class="surface-card" style="max-width:520px; text-align:center;">
        <h2 style="margin-bottom:0.5rem;">Could not connect to AI-901 backend</h2>
        <p style="font-size:0.9rem; color:var(--ink-secondary); margin-bottom:0.8rem;">${escapeHtml(err.message)}</p>
        <p style="font-size:0.82rem; color:var(--ink-muted);">Start the server with <code>python3 run.py</code> and refresh.</p>
      </div>
    `;
  }
}

init();
