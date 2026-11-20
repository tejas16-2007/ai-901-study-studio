/**
 * View 1: AI-901 Study Guides, Responsible AI Risk Mapper,
 * Model Parameter Visualizer, and Foundry SDK Code Samples.
 */

import { studyState } from "../state.js";
import { copyToClipboard, domainBadge, escapeHtml, renderInlineMd } from "../utils.js";

const RAI_SCENARIOS = [
  {
    id: "loan-bias",
    label: "Postal-code loan bias",
    scenario:
      "A credit approval model rejects qualified applicants from certain ZIP codes twice as often as similar applicants elsewhere.",
    principle: "Fairness",
    mitigation:
      "Audit training data for historical proxy bias, evaluate parity metrics across cohorts, and remove/mitigate biased features before deployment.",
  },
  {
    id: "dim-lighting",
    label: "Low-light warehouse sensor",
    scenario:
      "An autonomous forklift vision model struggles in dim corridors and fails to detect pallets reliably.",
    principle: "Reliability & Safety",
    mitigation:
      "Red-team under adverse edge cases, enforce confidence thresholds that trigger safe-stop fallbacks, and keep human supervisors in the loop.",
  },
  {
    id: "pii-prompt",
    label: "Clinical prompt leakage",
    scenario:
      "An internal healthcare assistant could expose patient medical numbers if an attacker injects adversarial instructions.",
    principle: "Privacy & Security",
    mitigation:
      "Enforce Microsoft Entra ID RBAC, private networking, PII redaction via Azure Language, and Prompt Shields in Azure AI Content Safety.",
  },
  {
    id: "captioning",
    label: "Hearing-impaired learners",
    scenario:
      "Recorded town-hall videos lack live captions and screen-reader image descriptions for employees with disabilities.",
    principle: "Inclusiveness",
    mitigation:
      "Integrate Azure Speech real-time captioning/multilingual translation and Vision dense captioning so all users can access the experience.",
  },
  {
    id: "ai-disclosure",
    label: "Undisclosed HR chatbot",
    scenario:
      "Employees assume they are chatting with a human HR representative and are unaware responses come from a generative model.",
    principle: "Transparency",
    mitigation:
      "Display a clear AI disclosure notice, link cited policy documents, and publish a Transparency Note documenting capabilities and limits.",
  },
  {
    id: "audit-owner",
    label: "Unowned escalation bot",
    scenario:
      "When an AI support agent issues an incorrect refund, no audit log or team owner exists to review or remediate the incident.",
    principle: "Accountability",
    mitigation:
      "Assign an executive/engineering owner, maintain tamper-evident audit trails of agent runs, and complete pre-release Responsible AI impact reviews.",
  },
];

const BASE_LOGITS = [
  { token: "Foundry", logit: 4.2 },
  { token: "Azure", logit: 3.5 },
  { token: "Copilot", logit: 2.6 },
  { token: "Cloud", logit: 1.9 },
  { token: "Quantum", logit: 0.7 },
];

function computeTokenDistribution(temperature, topP) {
  const safeTemp = Math.max(0.05, Number(temperature));
  const exps = BASE_LOGITS.map((item) => Math.exp(item.logit / safeTemp));
  const sum = exps.reduce((acc, v) => acc + v, 0);
  const probs = BASE_LOGITS.map((item, i) => ({
    token: item.token,
    prob: exps[i] / sum,
  }));

  let cumulative = 0;
  return probs.map((item, idx) => {
    const included = idx === 0 || cumulative < topP;
    cumulative += item.prob;
    return { ...item, included };
  });
}

export function renderGuidesView(container, curriculum, { onNavigate }) {
  let activeModuleId = curriculum.modules[0].id;
  let activeRaiId = RAI_SCENARIOS[0].id;
  let simTemp = 0.3;
  let simTopP = 0.9;

  function render() {
    const activeMod =
      curriculum.modules.find((m) => m.id === activeModuleId) || curriculum.modules[0];
    const doneCount = studyState.get().completedModules.length;
    const totalMods = curriculum.modules.length;
    const isModDone = studyState.isModuleComplete(activeMod.id);

    const d1Mods = curriculum.modules.filter((m) => m.domain_id === "domain-1");
    const d2Mods = curriculum.modules.filter((m) => m.domain_id === "domain-2");

    container.innerHTML = `
      <div class="page-intro">
        <div>
          <h1 id="guides-heading">Exam AI-901 Study Guides</h1>
          <p class="page-lead">
            Master all seven official syllabus modules for <strong>Microsoft Azure AI Fundamentals (AI-901)</strong> — from Responsible AI and model tuning to hands-on implementation in Microsoft Foundry.
          </p>
        </div>
        <div class="badge badge-neutral">${doneCount} / ${totalMods} modules completed</div>
      </div>

      <div class="blueprint-strip">
        <div class="blueprint-item">
          <div class="blueprint-item-head">
            <span class="badge badge-domain-1">Domain 1</span>
            <span class="blueprint-weight">40–45%</span>
          </div>
          <div class="blueprint-title">Identify AI concepts &amp; capabilities</div>
          <div class="blueprint-sub">Responsible AI · Model mechanics &amp; config · Core AI workloads</div>
        </div>
        <div class="blueprint-item">
          <div class="blueprint-item-head">
            <span class="badge badge-domain-2">Domain 2</span>
            <span class="blueprint-weight">55–60%</span>
          </div>
          <div class="blueprint-title">Implement AI solutions in Microsoft Foundry</div>
          <div class="blueprint-sub">Chat &amp; single agents · Text &amp; speech · Vision · Content Understanding</div>
        </div>
        <div class="blueprint-item">
          <div class="blueprint-item-head">
            <span class="badge badge-neutral">Exam Format</span>
            <span class="blueprint-weight">700 / 1000</span>
          </div>
          <div class="blueprint-title">Passing scaled score · 45 min</div>
          <div class="blueprint-sub">Replaced AI-900 on June 30, 2026 · Python &amp; Foundry SDK aware</div>
        </div>
      </div>

      <div class="guides-layout">
        <aside class="syllabus-rail" aria-label="AI-901 Syllabus Modules">
          <div class="rail-group">
            <div class="rail-group-title">
              <span>Domain 1 · Concepts</span>
              <span>40–45%</span>
            </div>
            ${d1Mods
              .map((m) => {
                const done = studyState.isModuleComplete(m.id);
                return `
                  <button
                    class="rail-btn ${m.id === activeMod.id ? "is-active" : ""}"
                    data-module-id="${m.id}"
                    type="button"
                  >
                    <span class="rail-num">${escapeHtml(m.number)}</span>
                    <span class="rail-label">${escapeHtml(m.title)}</span>
                    <span class="rail-check ${done ? "is-done" : ""}" aria-hidden="true">${done ? "✓" : ""}</span>
                  </button>
                `;
              })
              .join("")}
          </div>

          <div class="rail-group">
            <div class="rail-group-title">
              <span>Domain 2 · Microsoft Foundry</span>
              <span>55–60%</span>
            </div>
            ${d2Mods
              .map((m) => {
                const done = studyState.isModuleComplete(m.id);
                return `
                  <button
                    class="rail-btn ${m.id === activeMod.id ? "is-active" : ""}"
                    data-module-id="${m.id}"
                    type="button"
                  >
                    <span class="rail-num">${escapeHtml(m.number)}</span>
                    <span class="rail-label">${escapeHtml(m.title)}</span>
                    <span class="rail-check ${done ? "is-done" : ""}" aria-hidden="true">${done ? "✓" : ""}</span>
                  </button>
                `;
              })
              .join("")}
          </div>
        </aside>

        <article class="surface-card module-pane" id="active-module-article">
          <div class="module-header-bar">
            <div>
              <div style="display:flex; gap:0.45rem; align-items:center; flex-wrap:wrap;">
                ${domainBadge(activeMod.domain_id)}
                <span class="badge badge-neutral">Module ${escapeHtml(activeMod.number)}</span>
                <span class="badge badge-warn">${escapeHtml(activeMod.exam_focus)}</span>
              </div>
              <h2 class="module-title">${escapeHtml(activeMod.title)}</h2>
              <p class="module-overview">${escapeHtml(activeMod.overview)}</p>
            </div>
            <button
              class="btn ${isModDone ? "btn-secondary" : "btn-primary"} btn-sm"
              id="toggle-module-complete"
              type="button"
            >
              ${isModDone ? "✓ Completed" : "Mark Module Studied"}
            </button>
          </div>

          <div class="concepts-grid">
            ${activeMod.key_concepts
              .map(
                (c) => `
                  <div class="concept-tile">
                    <h3>${escapeHtml(c.term)}</h3>
                    <p>${renderInlineMd(c.detail)}</p>
                  </div>
                `
              )
              .join("")}
          </div>

          ${renderModuleWidget(activeMod)}

          <div class="tips-panel">
            <h3>Exam AI-901 Fast-Recognition Tips</h3>
            <ul class="tips-list">
              ${activeMod.exam_tips.map((tip) => `<li>${renderInlineMd(tip)}</li>`).join("")}
            </ul>
          </div>

          ${
            activeMod.code_snippet
              ? `
                <div class="code-panel">
                  <div class="code-panel-head">
                    <span>${escapeHtml(activeMod.code_snippet.title)}</span>
                    <div style="display:flex; gap:0.45rem;">
                      <button class="btn btn-subtle btn-sm" id="copy-sdk-snippet" type="button">Copy Python</button>
                      <button class="btn btn-primary btn-sm" id="open-sandbox-from-guide" type="button">Try in Foundry Sandbox</button>
                    </div>
                  </div>
                  <pre><code>${escapeHtml(activeMod.code_snippet.code)}</code></pre>
                </div>
              `
              : ""
          }

          <div style="display:flex; justify-content:space-between; gap:0.75rem; flex-wrap:wrap; padding-top:0.5rem; border-top:1px solid var(--border-subtle);">
            <button class="btn btn-secondary btn-sm" id="guide-to-flashcards" type="button">
              Drill Flashcards for This Domain
            </button>
            <button class="btn btn-primary btn-sm" id="guide-next-module" type="button">
              Next Module →
            </button>
          </div>
        </article>
      </div>
    `;

    bindEvents(activeMod);
  }

  function renderModuleWidget(mod) {
    if (mod.interactive_widget === "responsible_ai_checklist") {
      const current = RAI_SCENARIOS.find((s) => s.id === activeRaiId) || RAI_SCENARIOS[0];
      return `
        <div class="widget-box" id="rai-widget">
          <div class="widget-head">
            <h3>Interactive Responsible AI Scenario Mapper</h3>
            <span class="eyebrow">Pick a real deployment risk</span>
          </div>
          <div class="rai-scenario-tabs">
            ${RAI_SCENARIOS.map(
              (s) => `
                <button
                  class="chip-btn ${s.id === current.id ? "is-active" : ""}"
                  data-rai-id="${s.id}"
                  type="button"
                >${escapeHtml(s.label)}</button>
              `
            ).join("")}
          </div>
          <p style="font-size:0.9rem; color:var(--ink-primary); margin-bottom:0.65rem;">
            <strong>Scenario:</strong> ${escapeHtml(current.scenario)}
          </p>
          <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.45rem;">
            <span class="badge badge-domain-1">Primary Principle: ${escapeHtml(current.principle)}</span>
          </div>
          <p style="font-size:0.86rem; color:var(--ink-secondary);">
            <strong>Azure / Foundry Mitigation:</strong> ${escapeHtml(current.mitigation)}
          </p>
        </div>
      `;
    }

    if (mod.interactive_widget === "parameter_sandbox") {
      const dist = computeTokenDistribution(simTemp, simTopP);
      const regime =
        simTemp <= 0.3
          ? "Deterministic — ideal for JSON extraction, code, and factual RAG"
          : simTemp <= 0.85
          ? "Balanced — great for conversational assistants and explanations"
          : "Exploratory — high variety for creative brainstorming";
      return `
        <div class="widget-box" id="param-widget">
          <div class="widget-head">
            <h3>Interactive Decoding Simulator (Temperature &amp; Top-P)</h3>
            <span class="badge badge-neutral">${escapeHtml(regime)}</span>
          </div>
          <p style="font-size:0.84rem; color:var(--ink-muted); margin-bottom:0.8rem;">
            Prompt: <code>"To deploy and evaluate an AI agent on Azure, open Microsoft ___"</code> — watch next-token sampling probabilities shift as you tune decoding parameters.
          </p>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
            <div class="field-group" style="margin-bottom:0;">
              <label class="field-label" for="guide-temp-slider">
                <span>temperature</span>
                <span class="eyebrow" id="guide-temp-val">${simTemp.toFixed(2)}</span>
              </label>
              <input id="guide-temp-slider" type="range" min="0.05" max="1.8" step="0.05" value="${simTemp}" />
            </div>
            <div class="field-group" style="margin-bottom:0;">
              <label class="field-label" for="guide-topp-slider">
                <span>top_p (nucleus cutoff)</span>
                <span class="eyebrow" id="guide-topp-val">${simTopP.toFixed(2)}</span>
              </label>
              <input id="guide-topp-slider" type="range" min="0.2" max="1.0" step="0.05" value="${simTopP}" />
            </div>
          </div>
          <div class="token-bars" id="guide-token-bars">
            ${dist
              .map(
                (row) => `
                  <div class="token-row">
                    <span class="token-word">"${escapeHtml(row.token)}"</span>
                    <div class="bar-track">
                      <div class="bar-fill ${row.included ? "" : "is-muted"}" style="width:${Math.max(2, Math.round(row.prob * 100))}%"></div>
                    </div>
                    <span class="token-pct">${(row.prob * 100).toFixed(1)}%${row.included ? "" : " ✕"}</span>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
      `;
    }

    return "";
  }

  function bindEvents(activeMod) {
    container.querySelectorAll("[data-module-id]").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeModuleId = btn.dataset.moduleId;
        render();
      });
    });

    const toggleBtn = container.querySelector("#toggle-module-complete");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", () => {
        studyState.toggleModuleComplete(activeMod.id);
        render();
      });
    }

    container.querySelectorAll("[data-rai-id]").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeRaiId = btn.dataset.raiId;
        render();
      });
    });

    const tempSlider = container.querySelector("#guide-temp-slider");
    const toppSlider = container.querySelector("#guide-topp-slider");
    if (tempSlider && toppSlider) {
      const updateBars = () => {
        simTemp = parseFloat(tempSlider.value);
        simTopP = parseFloat(toppSlider.value);
        const valT = container.querySelector("#guide-temp-val");
        const valP = container.querySelector("#guide-topp-val");
        if (valT) valT.textContent = simTemp.toFixed(2);
        if (valP) valP.textContent = simTopP.toFixed(2);
        const barsEl = container.querySelector("#guide-token-bars");
        if (barsEl) {
          const dist = computeTokenDistribution(simTemp, simTopP);
          barsEl.innerHTML = dist
            .map(
              (row) => `
                <div class="token-row">
                  <span class="token-word">"${escapeHtml(row.token)}"</span>
                  <div class="bar-track">
                    <div class="bar-fill ${row.included ? "" : "is-muted"}" style="width:${Math.max(2, Math.round(row.prob * 100))}%"></div>
                  </div>
                  <span class="token-pct">${(row.prob * 100).toFixed(1)}%${row.included ? "" : " ✕"}</span>
                </div>
              `
            )
            .join("");
        }
      };
      tempSlider.addEventListener("input", updateBars);
      toppSlider.addEventListener("input", updateBars);
    }

    const copyBtn = container.querySelector("#copy-sdk-snippet");
    if (copyBtn && activeMod.code_snippet) {
      copyBtn.addEventListener("click", () => {
        copyToClipboard(activeMod.code_snippet.code, "Python Foundry SDK snippet copied!");
      });
    }

    const sandboxBtn = container.querySelector("#open-sandbox-from-guide");
    if (sandboxBtn) {
      sandboxBtn.addEventListener("click", () => onNavigate("sandbox"));
    }

    const fcBtn = container.querySelector("#guide-to-flashcards");
    if (fcBtn) {
      fcBtn.addEventListener("click", () => onNavigate("flashcards"));
    }

    const nextBtn = container.querySelector("#guide-next-module");
    if (nextBtn) {
      const idx = curriculum.modules.findIndex((m) => m.id === activeMod.id);
      const nextMod = curriculum.modules[(idx + 1) % curriculum.modules.length];
      nextBtn.textContent = `Next: ${nextMod.number} ${nextMod.title} →`;
      nextBtn.addEventListener("click", () => {
        activeModuleId = nextMod.id;
        render();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  render();
}
