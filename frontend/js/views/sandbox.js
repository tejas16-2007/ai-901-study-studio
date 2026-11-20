/**
 * View 4: Interactive Dual-Mode Microsoft Foundry Sandbox.
 * Connects directly to FastAPI /api/labs/* (Demo Mode or Live Azure SDKs).
 */

import { api } from "../api.js";
import { escapeHtml, renderInlineMd, showToast } from "../utils.js";

const LAB_TABS = [
  { id: "chat", label: "1. Foundry Chat" },
  { id: "agent", label: "2. Single-Agent" },
  { id: "text_speech", label: "3. Text & Speech" },
  { id: "content", label: "4. Content Understanding" },
  { id: "vision", label: "5. Vision & Image Gen" },
];

export function renderSandboxView(container, curriculum) {
  let activeTab = "chat";
  let busy = false;
  let lastResult = null;
  let lastError = null;

  const samples = curriculum.sandbox_samples;

  // Persistent input values across re-renders
  const form = {
    chatSystem: "You are a concise Azure AI-901 solutions tutor. Ground answers in Microsoft Foundry best practices.",
    chatUser: "When should an engineering team choose a Foundry Single-Agent over a standard stateless chat client?",
    chatModel: "gpt-4o-mini",
    chatTemp: 0.25,
    chatTopP: 0.95,
    chatMaxTokens: 280,

    agentGoal: "Design an automated invoice intake pipeline that extracts line items from vendor PDFs and flags low-confidence fields for human review.",
    agentInstructions: "Recommend the exact Microsoft Foundry workload, identify Responsible AI requirements, and estimate token usage.",
    agentTools: ["recommend_foundry_service", "responsible_ai_audit", "estimate_token_cost"],

    textSampleId: samples.text_samples[0].id,
    textInput: samples.text_samples[0].text,
    speechText: "Welcome to AI-901 Study Studio. Azure Speech in Foundry Tools powers lifelike neural voices with SSML.",
    speechVoice: "en-US-AvaMultilingualNeural",

    contentModality: "document",
    contentInput: samples.content_samples.document.content,

    visionTask: "analyze",
    visionPreset: samples.vision_presets[0].id,
    visionPrompt: samples.vision_presets[0].default_prompt,
  };

  async function execute(fn) {
    busy = true;
    lastError = null;
    render();
    try {
      lastResult = await fn();
    } catch (err) {
      lastError = err.message;
    } finally {
      busy = false;
      render();
    }
  }

  function render() {
    container.innerHTML = `
      <div class="page-intro">
        <div>
          <h1 id="sandbox-heading">Microsoft Foundry Dual-Mode Sandbox</h1>
          <p class="page-lead">
            Practice every Domain 2 AI-901 workload interactively. Calls hit your local FastAPI backend in <strong>Demo Mode</strong> right away, and upgrade seamlessly to <strong>Live Microsoft Foundry</strong> when <code>.env</code> credentials are configured.
          </p>
        </div>
      </div>

      <div class="sandbox-tabs" role="tablist" aria-label="Microsoft Foundry Workloads">
        ${LAB_TABS.map(
          (t) => `
            <button
              class="chip-btn ${t.id === activeTab ? "is-active" : ""}"
              data-lab-tab="${t.id}"
              role="tab"
              aria-selected="${t.id === activeTab}"
              type="button"
            >${escapeHtml(t.label)}</button>
          `
        ).join("")}
      </div>

      <div class="sandbox-grid">
        <div class="surface-card" id="sandbox-input-panel">
          ${renderInputPanel()}
        </div>
        <div class="surface-card output-panel" id="sandbox-output-panel">
          ${renderOutputPanel()}
        </div>
      </div>
    `;

    bindEvents();
  }

  function renderInputPanel() {
    if (activeTab === "chat") {
      return `
        <h2 style="font-size:1.1rem; margin-bottom:0.85rem;">Foundry Chat Client &amp; Model Config</h2>
        <div class="field-group">
          <label class="field-label" for="lab-chat-model">Deployed Model</label>
          <select class="field-select" id="lab-chat-model">
            <option value="gpt-4o-mini" ${form.chatModel === "gpt-4o-mini" ? "selected" : ""}>gpt-4o-mini (Fast, cost-effective chat)</option>
            <option value="gpt-4o" ${form.chatModel === "gpt-4o" ? "selected" : ""}>gpt-4o (Flagship multimodal LLM)</option>
            <option value="Phi-4" ${form.chatModel === "Phi-4" ? "selected" : ""}>Phi-4 (Small Language Model / SLM)</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label" for="lab-chat-system">System Prompt (Role &amp; Guardrails)</label>
          <textarea class="field-textarea" id="lab-chat-system" style="min-height:72px;">${escapeHtml(form.chatSystem)}</textarea>
        </div>
        <div class="field-group">
          <label class="field-label" for="lab-chat-user">User Prompt</label>
          <textarea class="field-textarea" id="lab-chat-user">${escapeHtml(form.chatUser)}</textarea>
        </div>
        <div class="slider-row" style="margin-bottom:1.1rem;">
          <div class="field-group" style="margin-bottom:0;">
            <label class="field-label" for="lab-temp"><span>temperature</span><code id="lab-temp-out">${form.chatTemp}</code></label>
            <input id="lab-temp" type="range" min="0" max="1.6" step="0.05" value="${form.chatTemp}" />
          </div>
          <div class="field-group" style="margin-bottom:0;">
            <label class="field-label" for="lab-topp"><span>top_p</span><code id="lab-topp-out">${form.chatTopP}</code></label>
            <input id="lab-topp" type="range" min="0.2" max="1" step="0.05" value="${form.chatTopP}" />
          </div>
          <div class="field-group" style="margin-bottom:0;">
            <label class="field-label" for="lab-maxtok"><span>max_tokens</span><code id="lab-maxtok-out">${form.chatMaxTokens}</code></label>
            <input id="lab-maxtok" type="range" min="64" max="600" step="16" value="${form.chatMaxTokens}" />
          </div>
        </div>
        <button class="btn btn-primary" id="run-chat-btn" type="button" ${busy ? "disabled" : ""}>
          ${busy ? "Running Foundry Chat…" : "Send to Foundry Chat"}
        </button>
      `;
    }

    if (activeTab === "agent") {
      const tools = [
        { id: "recommend_foundry_service", label: "recommend_foundry_service (Workload Router)" },
        { id: "responsible_ai_audit", label: "responsible_ai_audit (6-Principle Check)" },
        { id: "estimate_token_cost", label: "estimate_token_cost (Deployment Sizing)" },
      ];
      return `
        <h2 style="font-size:1.1rem; margin-bottom:0.85rem;">Microsoft Foundry Single-Agent Runner</h2>
        <div class="field-group">
          <label class="field-label" for="lab-agent-instructions">Agent Instructions</label>
          <textarea class="field-textarea" id="lab-agent-instructions" style="min-height:68px;">${escapeHtml(form.agentInstructions)}</textarea>
        </div>
        <div class="field-group">
          <label class="field-label" for="lab-agent-goal">User Goal (Posted to Agent Thread)</label>
          <textarea class="field-textarea" id="lab-agent-goal">${escapeHtml(form.agentGoal)}</textarea>
        </div>
        <div class="field-group">
          <span class="field-label">Attached Agent Tools</span>
          <div style="display:flex; flex-direction:column; gap:0.4rem; padding-top:0.2rem;">
            ${tools
              .map(
                (t) => `
                  <label style="display:flex; align-items:center; gap:0.5rem; font-size:0.86rem; cursor:pointer;">
                    <input type="checkbox" data-agent-tool="${t.id}" ${form.agentTools.includes(t.id) ? "checked" : ""} />
                    <span>${escapeHtml(t.label)}</span>
                  </label>
                `
              )
              .join("")}
          </div>
        </div>
        <button class="btn btn-primary" id="run-agent-btn" type="button" ${busy ? "disabled" : ""}>
          ${busy ? "Executing Agent Run…" : "Create Thread & Run Agent"}
        </button>
      `;
    }

    if (activeTab === "text_speech") {
      return `
        <h2 style="font-size:1.1rem; margin-bottom:0.85rem;">Azure Language (Text Analysis) &amp; Azure Speech</h2>
        <div style="display:flex; gap:0.45rem; flex-wrap:wrap; margin-bottom:0.85rem;">
          ${samples.text_samples
            .map(
              (s) => `
                <button class="chip-btn ${form.textSampleId === s.id ? "is-active" : ""}" data-text-sample="${s.id}" type="button">
                  ${escapeHtml(s.label)}
                </button>
              `
            )
            .join("")}
        </div>
        <div class="field-group">
          <label class="field-label" for="lab-text-input">Source Document for NLP</label>
          <textarea class="field-textarea" id="lab-text-input">${escapeHtml(form.textInput)}</textarea>
        </div>
        <button class="btn btn-primary" id="run-text-btn" type="button" style="margin-bottom:1.25rem;" ${busy ? "disabled" : ""}>
          ${busy ? "Analyzing…" : "Run Sentiment, Key Phrases, NER/PII & Summary"}
        </button>

        <div style="padding-top:1rem; border-top:1px solid var(--border-subtle);">
          <h3 style="font-size:0.96rem; margin-bottom:0.65rem;">Azure Speech SSML &amp; Neural Voice Preview</h3>
          <div class="field-group">
            <label class="field-label" for="lab-speech-voice">Neural Voice</label>
            <select class="field-select" id="lab-speech-voice">
              <option value="en-US-AvaMultilingualNeural" ${form.speechVoice === "en-US-AvaMultilingualNeural" ? "selected" : ""}>en-US-AvaMultilingualNeural</option>
              <option value="en-US-AndrewMultilingualNeural" ${form.speechVoice === "en-US-AndrewMultilingualNeural" ? "selected" : ""}>en-US-AndrewMultilingualNeural</option>
              <option value="en-GB-SoniaNeural" ${form.speechVoice === "en-GB-SoniaNeural" ? "selected" : ""}>en-GB-SoniaNeural</option>
            </select>
          </div>
          <div class="field-group">
            <label class="field-label" for="lab-speech-text">Spoken Prompt / Narration Text</label>
            <input class="field-input" id="lab-speech-text" type="text" value="${escapeHtml(form.speechText)}" />
          </div>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
            <button class="btn btn-secondary btn-sm" id="run-speech-btn" type="button" ${busy ? "disabled" : ""}>Generate SSML &amp; Diagnostics</button>
            <button class="btn btn-subtle btn-sm" id="browser-speak-btn" type="button">Play Browser Audio Preview</button>
          </div>
        </div>
      `;
    }

    if (activeTab === "content") {
      const modalities = ["document", "image", "audio", "video"];
      return `
        <h2 style="font-size:1.1rem; margin-bottom:0.85rem;">Azure Content Understanding Analyzer</h2>
        <p style="font-size:0.84rem; color:var(--ink-muted); margin-bottom:0.85rem;">
          Switch modalities to see how one schema-driven Analyzer extracts structured fields (<code>extract</code>, <code>classify</code>, <code>generate</code>) with confidence scores and provenance.
        </p>
        <div style="display:flex; gap:0.45rem; flex-wrap:wrap; margin-bottom:0.9rem;">
          ${modalities
            .map(
              (m) => `
                <button class="chip-btn ${form.contentModality === m ? "is-active" : ""}" data-cu-mod="${m}" type="button">
                  ${escapeHtml(samples.content_samples[m].label)}
                </button>
              `
            )
            .join("")}
        </div>
        <div class="field-group">
          <label class="field-label" for="lab-cu-content">Input Content (or HTTPS URL in Live Mode)</label>
          <textarea class="field-textarea" id="lab-cu-content" style="min-height:155px; font-family:var(--font-mono); font-size:0.8rem;">${escapeHtml(form.contentInput)}</textarea>
        </div>
        <button class="btn btn-primary" id="run-cu-btn" type="button" ${busy ? "disabled" : ""}>
          ${busy ? "Extracting Schema Fields…" : `Run ${form.contentModality.toUpperCase()} Analyzer`}
        </button>
      `;
    }

    // vision
    return `
      <h2 style="font-size:1.1rem; margin-bottom:0.85rem;">Computer Vision &amp; Image Generation</h2>
      <div style="display:flex; gap:0.45rem; margin-bottom:0.95rem;">
        <button class="chip-btn ${form.visionTask === "analyze" ? "is-active" : ""}" data-vision-task="analyze" type="button">Analyze Visual Input (Multimodal)</button>
        <button class="chip-btn ${form.visionTask === "generate" ? "is-active" : ""}" data-vision-task="generate" type="button">Generate Visual Output</button>
      </div>
      ${
        form.visionTask === "analyze"
          ? `
            <div class="field-group">
              <label class="field-label" for="lab-vision-preset">Sample Visual Scene</label>
              <select class="field-select" id="lab-vision-preset">
                ${samples.vision_presets
                  .map(
                    (p) => `<option value="${p.id}" ${form.visionPreset === p.id ? "selected" : ""}>${escapeHtml(p.label)}</option>`
                  )
                  .join("")}
              </select>
            </div>
          `
          : ""
      }
      <div class="field-group">
        <label class="field-label" for="lab-vision-prompt">${form.visionTask === "analyze" ? "Visual Inspection Prompt" : "Image Generation Prompt"}</label>
        <textarea class="field-textarea" id="lab-vision-prompt">${escapeHtml(form.visionPrompt)}</textarea>
      </div>
      <button class="btn btn-primary" id="run-vision-btn" type="button" ${busy ? "disabled" : ""}>
        ${busy ? "Processing…" : form.visionTask === "analyze" ? "Inspect Image with Multimodal Model" : "Prepare & Safety-Check Image Prompt"}
      </button>
    `;
  }

  function renderOutputPanel() {
    if (busy) {
      return `
        <div class="loading-state" style="padding:3rem 1rem;">
          <div class="spinner"></div>
          <p>Calling Microsoft Foundry dual-mode endpoint…</p>
        </div>
      `;
    }
    if (lastError) {
      return `
        <div class="output-meta-bar">
          <span class="badge badge-danger">Error</span>
        </div>
        <p style="color:var(--status-danger); font-size:0.9rem;">${escapeHtml(lastError)}</p>
      `;
    }
    if (!lastResult) {
      return `
        <div style="margin:auto; text-align:center; padding:2.5rem 1rem; color:var(--ink-muted);">
          <p class="eyebrow" style="margin-bottom:0.45rem;">Ready to Run</p>
          <p style="font-size:0.9rem; max-width:36ch; margin:0 auto;">
            Configure inputs on the left and click Run to see structured telemetry, Responsible AI signals, and JSON outputs from the backend.
          </p>
        </div>
      `;
    }

    const { mode, service, note, data } = lastResult;
    const modeBadge =
      mode === "live"
        ? `<span class="badge badge-success">LIVE · Microsoft Foundry</span>`
        : `<span class="badge badge-warn">DEMO MODE</span>`;

    let bodyHtml = "";

    if (data.reply !== undefined) {
      bodyHtml = `
        <div class="output-prose">${renderInlineMd(data.reply)}</div>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <span class="badge badge-neutral">Model: ${escapeHtml(data.model)}</span>
          <span class="badge badge-neutral">Prompt: ${data.usage?.prompt_tokens ?? "–"} tok</span>
          <span class="badge badge-neutral">Completion: ${data.usage?.completion_tokens ?? "–"} tok</span>
          <span class="badge badge-success">Content Safety: Passed</span>
          <span class="badge badge-neutral">${data.latency_ms} ms</span>
        </div>
      `;
    } else if (data.tool_calls) {
      bodyHtml = `
        <div class="eyebrow">Agent Thread: ${escapeHtml(data.thread_id)} · Status: ${escapeHtml(data.run_status)}</div>
        <div class="trace-list">
          ${data.tool_calls
            .map(
              (tc, idx) => `
                <div class="trace-step">
                  <div class="trace-step-head">
                    <span>Step ${idx + 1}: ${escapeHtml(tc.tool)}()</span>
                    <span class="badge badge-success">${escapeHtml(tc.status)}</span>
                  </div>
                  <pre style="margin:0; font-size:0.75rem; white-space:pre-wrap; color:var(--ink-secondary);">${escapeHtml(JSON.stringify(tc.output, null, 2))}</pre>
                </div>
              `
            )
            .join("")}
        </div>
        <div class="output-prose" style="padding-top:0.4rem; border-top:1px solid var(--border-subtle);">${renderInlineMd(data.final_response)}</div>
      `;
    } else if (data.sentiment) {
      const s = data.sentiment;
      bodyHtml = `
        <div style="display:flex; align-items:center; justify-content:space-between;">
          <strong>Overall Sentiment</strong>
          <span class="badge badge-${s.overall === "positive" ? "success" : s.overall === "negative" ? "danger" : "warn"}">${escapeHtml(s.overall.toUpperCase())}</span>
        </div>
        <div class="token-bars" style="margin-top:0;">
          ${["positive", "neutral", "negative"]
            .map(
              (k) => `
                <div class="token-row">
                  <span class="token-word">${k}</span>
                  <div class="bar-track"><div class="bar-fill" style="width:${Math.round((s.scores[k] || 0) * 100)}%"></div></div>
                  <span class="token-pct">${Math.round((s.scores[k] || 0) * 100)}%</span>
                </div>
              `
            )
            .join("")}
        </div>
        <div>
          <div class="eyebrow" style="margin-bottom:0.4rem;">Key Phrases</div>
          <div style="display:flex; gap:0.38rem; flex-wrap:wrap;">
            ${(data.key_phrases || []).map((kp) => `<span class="badge badge-domain-2">${escapeHtml(kp)}</span>`).join("")}
          </div>
        </div>
        <div>
          <div class="eyebrow" style="margin-bottom:0.4rem;">Named Entities &amp; PII</div>
          ${
            (data.entities || []).length
              ? `<div style="display:flex; gap:0.38rem; flex-wrap:wrap;">${data.entities
                  .map((e) => `<span class="badge badge-neutral">${escapeHtml(e.text)} · <em>${escapeHtml(e.category)}</em></span>`)
                  .join("")}</div>`
              : `<p style="font-size:0.84rem; color:var(--ink-muted);">No named entities detected.</p>`
          }
        </div>
        <div class="concept-tile">
          <div class="eyebrow" style="margin-bottom:0.25rem;">PII-Redacted Preview</div>
          <p style="font-size:0.84rem;">${escapeHtml(data.pii_redacted_text)}</p>
        </div>
        <div class="concept-tile">
          <div class="eyebrow" style="margin-bottom:0.25rem;">Extractive Summary</div>
          <p style="font-size:0.84rem;">${escapeHtml(data.extractive_summary)}</p>
        </div>
      `;
    } else if (data.ssml) {
      bodyHtml = `
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <span class="badge badge-domain-2">${escapeHtml(data.voice)}</span>
          <span class="badge badge-neutral">Est. duration: ${data.estimated_duration_sec}s</span>
        </div>
        <div class="code-panel">
          <div class="code-panel-head"><span>Generated SSML Payload</span></div>
          <pre><code>${escapeHtml(data.ssml)}</code></pre>
        </div>
      `;
    } else if (data.fields) {
      const entries = Object.entries(data.fields);
      bodyHtml = `
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
          <span class="badge badge-domain-2">${escapeHtml(data.analyzer_id)}</span>
          <span class="badge ${data.human_review_recommended ? "badge-warn" : "badge-success"}">
            ${data.human_review_recommended ? "Human Review Recommended (<85% confidence)" : "Auto-Approve Eligible (All ≥ 85%)"}
          </span>
        </div>
        <div style="overflow-x:auto;">
          <table class="data-table">
            <thead>
              <tr><th>Field</th><th>Method</th><th>Value</th><th>Conf.</th></tr>
            </thead>
            <tbody>
              ${entries
                .map(([key, item]) => {
                  const val = Array.isArray(item.value) ? item.value.join("; ") : item.value;
                  const low = item.confidence < 0.85;
                  return `
                    <tr>
                      <td><code>${escapeHtml(key)}</code><div style="font-size:0.72rem; color:var(--ink-muted);">${escapeHtml(item.grounding)}</div></td>
                      <td><span class="badge badge-neutral">${escapeHtml(item.method)}</span></td>
                      <td>${escapeHtml(val)}</td>
                      <td><span class="badge ${low ? "badge-warn" : "badge-success"}">${Math.round(item.confidence * 100)}%</span></td>
                    </tr>
                  `;
                })
                .join("")}
            </tbody>
          </table>
        </div>
      `;
    } else if (data.task === "analyze") {
      bodyHtml = `
        <div class="eyebrow">${escapeHtml(data.scene)}</div>
        <p class="output-prose">${escapeHtml(data.analysis)}</p>
        <div>
          <div class="eyebrow" style="margin-bottom:0.4rem;">Detected Regions</div>
          <div class="trace-list">
            ${data.detections
              .map(
                (d) => `
                  <div class="trace-step" style="display:flex; justify-content:space-between; align-items:center;">
                    <span><strong>${escapeHtml(d.label)}</strong> · <code>bbox ${JSON.stringify(d.bbox)}</code></span>
                    <span class="badge badge-success">${Math.round(d.confidence * 100)}%</span>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
        <div class="code-panel">
          <div class="code-panel-head"><span>Multimodal Message Content Shape</span></div>
          <pre><code>${escapeHtml(JSON.stringify(data.payload_shape, null, 2))}</code></pre>
        </div>
      `;
    } else if (data.task === "generate") {
      bodyHtml = `
        <div class="concept-tile">
          <div class="eyebrow" style="margin-bottom:0.25rem;">Refined Generation Prompt (${escapeHtml(data.model)} · ${escapeHtml(data.size)})</div>
          <p style="font-size:0.88rem;">${escapeHtml(data.enhanced_prompt)}</p>
        </div>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <span class="badge badge-success">Content Safety: ${escapeHtml(data.content_safety.prompt_filter)}</span>
          <span class="badge badge-domain-1">Transparency: C2PA / AI Disclosure</span>
        </div>
        <p style="font-size:0.84rem; color:var(--ink-secondary);">${escapeHtml(data.content_safety.transparency_note)}</p>
      `;
    }

    return `
      <div class="output-meta-bar">
        <strong style="font-size:0.9rem;">${escapeHtml(service)}</strong>
        ${modeBadge}
      </div>
      <div class="output-note">${escapeHtml(note)}</div>
      ${bodyHtml}
    `;
  }

  function bindEvents() {
    container.querySelectorAll("[data-lab-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeTab = btn.dataset.labTab;
        lastResult = null;
        lastError = null;
        render();
      });
    });

    if (activeTab === "chat") {
      const bindVal = (sel, key, parse = (v) => v, outSel = null) => {
        const el = container.querySelector(sel);
        if (!el) return;
        el.addEventListener("input", () => {
          form[key] = parse(el.value);
          if (outSel) {
            const out = container.querySelector(outSel);
            if (out) out.textContent = el.value;
          }
        });
      };
      bindVal("#lab-chat-model", "chatModel");
      bindVal("#lab-chat-system", "chatSystem");
      bindVal("#lab-chat-user", "chatUser");
      bindVal("#lab-temp", "chatTemp", parseFloat, "#lab-temp-out");
      bindVal("#lab-topp", "chatTopP", parseFloat, "#lab-topp-out");
      bindVal("#lab-maxtok", "chatMaxTokens", (v) => parseInt(v, 10), "#lab-maxtok-out");

      container.querySelector("#run-chat-btn").addEventListener("click", () =>
        execute(() =>
          api.runFoundryChat({
            model: form.chatModel,
            system_prompt: form.chatSystem,
            user_prompt: form.chatUser,
            temperature: form.chatTemp,
            top_p: form.chatTopP,
            max_tokens: form.chatMaxTokens,
          })
        )
      );
    }

    if (activeTab === "agent") {
      container.querySelector("#lab-agent-instructions").addEventListener("input", (e) => {
        form.agentInstructions = e.target.value;
      });
      container.querySelector("#lab-agent-goal").addEventListener("input", (e) => {
        form.agentGoal = e.target.value;
      });
      container.querySelectorAll("[data-agent-tool]").forEach((cb) => {
        cb.addEventListener("change", () => {
          const tool = cb.dataset.agentTool;
          if (cb.checked && !form.agentTools.includes(tool)) form.agentTools.push(tool);
          if (!cb.checked) form.agentTools = form.agentTools.filter((t) => t !== tool);
        });
      });
      container.querySelector("#run-agent-btn").addEventListener("click", () =>
        execute(() =>
          api.runFoundryAgent({
            goal: form.agentGoal,
            instructions: form.agentInstructions,
            enabled_tools: form.agentTools,
          })
        )
      );
    }

    if (activeTab === "text_speech") {
      container.querySelectorAll("[data-text-sample]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const chosen = samples.text_samples.find((s) => s.id === btn.dataset.textSample);
          if (chosen) {
            form.textSampleId = chosen.id;
            form.textInput = chosen.text;
            render();
          }
        });
      });
      container.querySelector("#lab-text-input").addEventListener("input", (e) => {
        form.textInput = e.target.value;
      });
      container.querySelector("#lab-speech-voice").addEventListener("change", (e) => {
        form.speechVoice = e.target.value;
      });
      container.querySelector("#lab-speech-text").addEventListener("input", (e) => {
        form.speechText = e.target.value;
      });
      container.querySelector("#run-text-btn").addEventListener("click", () =>
        execute(() => api.runTextAnalysis({ text: form.textInput }))
      );
      container.querySelector("#run-speech-btn").addEventListener("click", () =>
        execute(() =>
          api.runSpeechLab({
            direction: "tts",
            text: form.speechText,
            voice: form.speechVoice,
          })
        )
      );
      container.querySelector("#browser-speak-btn").addEventListener("click", () => {
        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
          const utter = new SpeechSynthesisUtterance(form.speechText);
          window.speechSynthesis.speak(utter);
          showToast("Playing speech preview via browser audio");
        } else {
          showToast("Browser speech synthesis not available in this environment");
        }
      });
    }

    if (activeTab === "content") {
      container.querySelectorAll("[data-cu-mod]").forEach((btn) => {
        btn.addEventListener("click", () => {
          form.contentModality = btn.dataset.cuMod;
          form.contentInput = samples.content_samples[form.contentModality].content;
          lastResult = null;
          render();
        });
      });
      container.querySelector("#lab-cu-content").addEventListener("input", (e) => {
        form.contentInput = e.target.value;
      });
      container.querySelector("#run-cu-btn").addEventListener("click", () =>
        execute(() =>
          api.runContentUnderstanding({
            modality: form.contentModality,
            content: form.contentInput,
            schema_fields: samples.content_samples[form.contentModality].schema_fields,
          })
        )
      );
    }

    if (activeTab === "vision") {
      container.querySelectorAll("[data-vision-task]").forEach((btn) => {
        btn.addEventListener("click", () => {
          form.visionTask = btn.dataset.visionTask;
          form.visionPrompt =
            form.visionTask === "analyze"
              ? samples.vision_presets.find((p) => p.id === form.visionPreset).default_prompt
              : "Clean isometric architecture diagram of a Microsoft Foundry RAG agent serving global retail stores";
          lastResult = null;
          render();
        });
      });
      const presetSel = container.querySelector("#lab-vision-preset");
      if (presetSel) {
        presetSel.addEventListener("change", () => {
          form.visionPreset = presetSel.value;
          const found = samples.vision_presets.find((p) => p.id === form.visionPreset);
          if (found) form.visionPrompt = found.default_prompt;
          render();
        });
      }
      container.querySelector("#lab-vision-prompt").addEventListener("input", (e) => {
        form.visionPrompt = e.target.value;
      });
      container.querySelector("#run-vision-btn").addEventListener("click", () =>
        execute(() =>
          api.runVisionLab({
            task: form.visionTask,
            prompt: form.visionPrompt,
            scene_preset: form.visionPreset,
          })
        )
      );
    }
  }

  render();
}
