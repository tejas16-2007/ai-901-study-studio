/**
 * View 3: Exam AI-901 Timed Practice Exam & Instant-Feedback Study Quiz
 * with Dual-Mode AI-901 Study Coach (/api/study-coach).
 */

import { api } from "../api.js";
import { studyState } from "../state.js";
import { domainBadge, escapeHtml, renderInlineMd, showToast } from "../utils.js";

const LETTERS = ["A", "B", "C", "D"];

function formatTimer(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

export function renderExamView(container, curriculum) {
  let phase = "launcher"; // "launcher" | "active" | "results"
  let mode = "timed"; // "timed" | "study"
  let studyDomain = "all";
  let questions = [];
  let currentIdx = 0;
  let answers = {}; // { [qId]: optionIndex }
  let flagged = new Set();
  let remainingSeconds = 45 * 60;
  let timerHandle = null;
  let lastResult = null;
  let coachCache = {}; // { [qId]: { loading, mode, service, coaching, error } }

  function stopTimer() {
    if (timerHandle) {
      clearInterval(timerHandle);
      timerHandle = null;
    }
  }

  function startSession(selectedMode, domainScope = "all") {
    stopTimer();
    mode = selectedMode;
    studyDomain = domainScope;
    const pool =
      domainScope === "all"
        ? [...curriculum.questions]
        : curriculum.questions.filter((q) => q.domain_id === domainScope);
    questions = pool;
    currentIdx = 0;
    answers = {};
    flagged = new Set();
    coachCache = {};
    remainingSeconds = selectedMode === "timed" ? 45 * 60 : 0;
    phase = "active";

    if (selectedMode === "timed") {
      timerHandle = setInterval(() => {
        remainingSeconds -= 1;
        const el = container.querySelector("#exam-timer-pill");
        if (el) {
          el.textContent = formatTimer(Math.max(0, remainingSeconds));
          el.classList.toggle("is-low", remainingSeconds <= 300);
        }
        if (remainingSeconds <= 0) {
          finishExam();
        }
      }, 1000);
    }
    render();
  }

  function finishExam() {
    stopTimer();
    let correct = 0;
    const domainTotals = {
      "domain-1": { correct: 0, total: 0 },
      "domain-2": { correct: 0, total: 0 },
    };

    for (const q of questions) {
      domainTotals[q.domain_id].total += 1;
      if (answers[q.id] === q.correct_index) {
        correct += 1;
        domainTotals[q.domain_id].correct += 1;
      }
    }

    const scaledScore = Math.round((correct / Math.max(1, questions.length)) * 1000);
    const passed = scaledScore >= 700;

    lastResult = {
      date: new Date().toLocaleString(),
      mode: mode === "timed" ? "Timed Mock Exam" : `Study Quiz (${studyDomain})`,
      scaledScore,
      correct,
      total: questions.length,
      passed,
      domainScores: domainTotals,
    };

    studyState.recordExamAttempt(lastResult);
    phase = "results";
    render();
  }

  async function askCoach(q, followUp = "") {
    coachCache[q.id] = { loading: true };
    render();
    try {
      const selectedIdx = answers[q.id];
      const resp = await api.askStudyCoach({
        question_id: q.id,
        question_text: q.question,
        selected_option: selectedIdx !== undefined ? q.options[selectedIdx] : null,
        correct_option: q.options[q.correct_index],
        topic: q.topic,
        follow_up: followUp || null,
      });
      coachCache[q.id] = {
        loading: false,
        mode: resp.mode,
        service: resp.service,
        note: resp.note,
        coaching: resp.data.coaching,
      };
    } catch (err) {
      coachCache[q.id] = {
        loading: false,
        error: err.message,
      };
    }
    render();
  }

  function render() {
    if (phase === "launcher") {
      renderLauncher();
    } else if (phase === "active") {
      renderActive();
    } else {
      renderResults();
    }
  }

  function renderLauncher() {
    const history = studyState.get().examHistory;
    const d1Count = curriculum.questions.filter((q) => q.domain_id === "domain-1").length;
    const d2Count = curriculum.questions.filter((q) => q.domain_id === "domain-2").length;

    container.innerHTML = `
      <div class="page-intro">
        <div>
          <h1 id="exam-heading">Exam AI-901 Practice Simulator</h1>
          <p class="page-lead">
            Test your readiness against 30 weighted exam-style scenarios (${d1Count} Domain 1 · ${d2Count} Domain 2) aligned to Microsoft's 700/1000 passing bar.
          </p>
        </div>
      </div>

      <div class="exam-launcher-grid">
        <div class="surface-card exam-mode-card">
          <div>
            <span class="badge badge-domain-2" style="margin-bottom:0.65rem;">Exam Simulation</span>
            <h2>Timed AI-901 Mock Exam</h2>
            <p style="font-size:0.9rem; color:var(--ink-secondary);">
              Full 30-question exam weighted 43% Domain 1 / 57% Domain 2 with a 45-minute timer, question flagging, and a complete domain score report at the end.
            </p>
            <div class="exam-specs">
              <span class="badge badge-neutral">30 questions</span>
              <span class="badge badge-neutral">45 min countdown</span>
              <span class="badge badge-neutral">Pass ≥ 700 / 1000</span>
            </div>
          </div>
          <button class="btn btn-primary" id="start-timed-exam" type="button">Start Timed Mock Exam</button>
        </div>

        <div class="surface-card exam-mode-card">
          <div>
            <span class="badge badge-domain-1" style="margin-bottom:0.65rem;">Guided Coaching</span>
            <h2>Study Quiz + AI-901 Coach</h2>
            <p style="font-size:0.9rem; color:var(--ink-secondary);">
              Untimed practice with immediate explanations after every question plus an interactive <strong>AI-901 Study Coach</strong> (Demo or Live Microsoft Foundry).
            </p>
            <div class="field-group" style="margin-top:0.85rem; margin-bottom:0;">
              <label class="field-label" for="study-domain-select">Focus Scope</label>
              <select class="field-select" id="study-domain-select">
                <option value="all">Both Domains (${curriculum.questions.length} questions)</option>
                <option value="domain-1">Domain 1: AI Concepts &amp; Responsible AI (${d1Count} questions)</option>
                <option value="domain-2">Domain 2: Microsoft Foundry Solutions (${d2Count} questions)</option>
              </select>
            </div>
          </div>
          <button class="btn btn-secondary" id="start-study-quiz" type="button">Launch Study Quiz</button>
        </div>
      </div>

      <div class="surface-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.85rem;">
          <h2 style="font-size:1.05rem;">Recent Practice Attempts</h2>
          <span class="eyebrow">${history.length} saved locally</span>
        </div>
        ${
          history.length === 0
            ? `<p style="font-size:0.88rem; color:var(--ink-muted);">No attempts yet. Complete a Timed Mock Exam or Study Quiz to track your scaled score trend.</p>`
            : `
              <div style="overflow-x:auto;">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Mode</th>
                      <th>Scaled Score</th>
                      <th>Accuracy</th>
                      <th>Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${history
                      .map(
                        (h) => `
                          <tr>
                            <td>${escapeHtml(h.date)}</td>
                            <td>${escapeHtml(h.mode)}</td>
                            <td><code>${h.scaledScore} / 1000</code></td>
                            <td>${h.correct} / ${h.total}</td>
                            <td><span class="badge ${h.passed ? "badge-success" : "badge-danger"}">${h.passed ? "PASS" : "REVIEW"}</span></td>
                          </tr>
                        `
                      )
                      .join("")}
                  </tbody>
                </table>
              </div>
            `
        }
      </div>
    `;

    container.querySelector("#start-timed-exam").addEventListener("click", () => startSession("timed", "all"));
    container.querySelector("#start-study-quiz").addEventListener("click", () => {
      const scope = container.querySelector("#study-domain-select").value;
      startSession("study", scope);
    });
  }

  function renderActive() {
    const q = questions[currentIdx];
    const selectedIdx = answers[q.id];
    const answeredCount = Object.keys(answers).length;
    const isFlagged = flagged.has(q.id);
    const showFeedback = mode === "study" && selectedIdx !== undefined;
    const coach = coachCache[q.id];

    container.innerHTML = `
      <div class="exam-shell">
        <div class="surface-card">
          <div class="exam-topbar">
            <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
              <span class="badge badge-neutral">Question ${currentIdx + 1} / ${questions.length}</span>
              ${domainBadge(q.domain_id)}
              <span class="eyebrow">${escapeHtml(q.topic)}</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              ${
                mode === "timed"
                  ? `<span class="timer-pill ${remainingSeconds <= 300 ? "is-low" : ""}" id="exam-timer-pill">${formatTimer(remainingSeconds)}</span>`
                  : `<span class="badge badge-domain-1">Study Mode</span>`
              }
              <button class="btn btn-subtle btn-sm" id="flag-q-btn" type="button">
                ${isFlagged ? "★ Flagged" : "☆ Flag"}
              </button>
            </div>
          </div>

          <h2 class="question-stem">${renderInlineMd(q.question)}</h2>

          <div class="options-list">
            ${q.options
              .map((opt, idx) => {
                let cls = "";
                if (showFeedback) {
                  if (idx === q.correct_index) cls = "is-correct";
                  else if (idx === selectedIdx) cls = "is-wrong";
                } else if (idx === selectedIdx) {
                  cls = "is-selected";
                }
                return `
                  <button
                    class="option-btn ${cls}"
                    data-opt-idx="${idx}"
                    type="button"
                    ${showFeedback ? "disabled" : ""}
                  >
                    <span class="option-letter">${LETTERS[idx]}</span>
                    <span>${renderInlineMd(opt)}</span>
                  </button>
                `;
              })
              .join("")}
          </div>

          ${
            showFeedback
              ? `
                <div class="explanation-box">
                  <div style="display:flex; align-items:center; justify-content:space-between; gap:0.6rem; margin-bottom:0.45rem;">
                    <strong style="color:${selectedIdx === q.correct_index ? "var(--status-success)" : "var(--status-danger)"};">
                      ${selectedIdx === q.correct_index ? "Correct!" : `Not quite — Correct answer is ${LETTERS[q.correct_index]}`}
                    </strong>
                    <button class="btn btn-secondary btn-sm" id="ask-coach-btn" type="button">
                      ${coach?.coaching ? "Refresh AI-901 Coach" : "Ask AI-901 Study Coach"}
                    </button>
                  </div>
                  <p>${renderInlineMd(q.explanation)}</p>
                </div>

                ${
                  coach
                    ? `
                      <div class="coach-panel">
                        <div style="display:flex; align-items:center; justify-content:space-between; gap:0.6rem; flex-wrap:wrap;">
                          <strong style="font-size:0.88rem;">AI-901 Study Coach</strong>
                          ${
                            coach.mode
                              ? `<span class="badge ${coach.mode === "live" ? "badge-success" : "badge-warn"}">${coach.mode === "live" ? "Live Foundry" : "Demo Mode"} · ${escapeHtml(coach.service)}</span>`
                              : ""
                          }
                        </div>
                        ${
                          coach.loading
                            ? `<p style="font-size:0.85rem; color:var(--ink-muted); margin-top:0.5rem;">Consulting AI-901 Study Coach…</p>`
                            : coach.error
                            ? `<p style="font-size:0.85rem; color:var(--status-danger); margin-top:0.5rem;">${escapeHtml(coach.error)}</p>`
                            : `
                              <div class="coach-response">${renderInlineMd(coach.coaching)}</div>
                              <div style="display:flex; gap:0.5rem; margin-top:0.75rem;">
                                <input class="field-input" id="coach-followup-input" type="text" placeholder="Ask a follow-up (e.g., why not PTU, or how does temperature affect this?)" />
                                <button class="btn btn-primary btn-sm" id="coach-followup-send" type="button">Ask</button>
                              </div>
                            `
                        }
                      </div>
                    `
                    : ""
                }
              `
              : ""
          }

          <div style="display:flex; justify-content:space-between; gap:0.75rem; margin-top:1.35rem; padding-top:1rem; border-top:1px solid var(--border-subtle); flex-wrap:wrap;">
            <button class="btn btn-secondary btn-sm" id="exam-prev-btn" type="button" ${currentIdx === 0 ? "disabled" : ""}>← Previous</button>
            <div style="display:flex; gap:0.5rem;">
              ${
                currentIdx < questions.length - 1
                  ? `<button class="btn btn-primary btn-sm" id="exam-next-btn" type="button">Next Question →</button>`
                  : `<button class="btn btn-primary btn-sm" id="exam-submit-btn-main" type="button">Finish &amp; Score Exam</button>`
              }
            </div>
          </div>
        </div>

        <aside class="surface-card" style="padding:1.1rem;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="font-size:0.94rem;">Question Navigator</h3>
            <span class="eyebrow">${answeredCount}/${questions.length}</span>
          </div>
          <div class="navigator-grid">
            ${questions
              .map((item, i) => {
                const cls = [
                  i === currentIdx ? "is-current" : "",
                  answers[item.id] !== undefined ? "is-answered" : "",
                  flagged.has(item.id) ? "is-flagged" : "",
                ]
                  .filter(Boolean)
                  .join(" ");
                return `<button class="nav-q-btn ${cls}" data-jump-idx="${i}" type="button">${i + 1}</button>`;
              })
              .join("")}
          </div>
          <button class="btn btn-primary" id="exam-finish-btn" type="button" style="width:100%; margin-bottom:0.5rem;">
            Submit &amp; Score
          </button>
          <button class="btn btn-subtle btn-sm" id="exam-exit-btn" type="button" style="width:100%;">
            Exit to Launcher
          </button>
        </aside>
      </div>
    `;

    container.querySelectorAll("[data-opt-idx]").forEach((btn) => {
      btn.addEventListener("click", () => {
        answers[q.id] = Number(btn.dataset.optIdx);
        render();
      });
    });

    container.querySelector("#flag-q-btn").addEventListener("click", () => {
      if (flagged.has(q.id)) flagged.delete(q.id);
      else flagged.add(q.id);
      render();
    });

    const prevBtn = container.querySelector("#exam-prev-btn");
    if (prevBtn) prevBtn.addEventListener("click", () => { currentIdx -= 1; render(); });

    const nextBtn = container.querySelector("#exam-next-btn");
    if (nextBtn) nextBtn.addEventListener("click", () => { currentIdx += 1; render(); });

    const mainSubmit = container.querySelector("#exam-submit-btn-main");
    if (mainSubmit) mainSubmit.addEventListener("click", finishExam);

    container.querySelector("#exam-finish-btn").addEventListener("click", finishExam);
    container.querySelector("#exam-exit-btn").addEventListener("click", () => {
      stopTimer();
      phase = "launcher";
      render();
    });

    container.querySelectorAll("[data-jump-idx]").forEach((btn) => {
      btn.addEventListener("click", () => {
        currentIdx = Number(btn.dataset.jumpIdx);
        render();
      });
    });

    const coachBtn = container.querySelector("#ask-coach-btn");
    if (coachBtn) coachBtn.addEventListener("click", () => askCoach(q));

    const followSend = container.querySelector("#coach-followup-send");
    const followInput = container.querySelector("#coach-followup-input");
    if (followSend && followInput) {
      followSend.addEventListener("click", () => {
        const val = followInput.value.trim();
        if (!val) return showToast("Type a follow-up question first");
        askCoach(q, val);
      });
    }
  }

  function renderResults() {
    const r = lastResult;
    const d1 = r.domainScores["domain-1"];
    const d2 = r.domainScores["domain-2"];
    const d1Pct = d1.total ? Math.round((d1.correct / d1.total) * 100) : 0;
    const d2Pct = d2.total ? Math.round((d2.correct / d2.total) * 100) : 0;

    container.innerHTML = `
      <div class="surface-card" style="margin-bottom:1.25rem;">
        <div class="score-hero">
          <div>
            <span class="badge ${r.passed ? "badge-success" : "badge-danger"}" style="margin-bottom:0.5rem;">
              ${r.passed ? "PASSED · Ready for AI-901" : "BELOW 700 · Keep Drilling"}
            </span>
            <h1 id="exam-heading" style="font-size:1.65rem;">Practice Exam Score Report</h1>
            <p style="font-size:0.9rem; color:var(--ink-secondary); margin-top:0.25rem;">
              ${escapeHtml(r.mode)} · ${r.correct} of ${r.total} questions correct · Microsoft passing threshold is 700/1000.
            </p>
          </div>
          <div style="text-align:right;">
            <div class="score-number ${r.passed ? "is-pass" : "is-fail"}">${r.scaledScore}</div>
            <div class="eyebrow">out of 1000</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:1rem; margin-bottom:1.25rem;">
          <div class="concept-tile">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
              <strong>Domain 1 · AI Concepts (40–45%)</strong>
              <code>${d1.correct}/${d1.total} (${d1Pct}%)</code>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:${d1Pct}%; background:var(--accent-domain1);"></div></div>
          </div>
          <div class="concept-tile">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
              <strong>Domain 2 · Microsoft Foundry (55–60%)</strong>
              <code>${d2.correct}/${d2.total} (${d2Pct}%)</code>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:${d2Pct}%;"></div></div>
          </div>
        </div>

        <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
          <button class="btn btn-primary btn-sm" id="retake-exam-btn" type="button">Retake Practice Exam</button>
          <button class="btn btn-secondary btn-sm" id="back-launcher-btn" type="button">Back to Exam Launcher</button>
        </div>
      </div>

      <div class="surface-card">
        <h2 style="font-size:1.1rem; margin-bottom:1rem;">Question-by-Question Review</h2>
        <div style="display:flex; flex-direction:column; gap:0.9rem;">
          ${questions
            .map((q, idx) => {
              const sel = answers[q.id];
              const ok = sel === q.correct_index;
              return `
                <div class="concept-tile">
                  <div style="display:flex; justify-content:space-between; gap:0.5rem; margin-bottom:0.4rem; flex-wrap:wrap;">
                    <span class="eyebrow">Q${idx + 1} · ${escapeHtml(q.topic)}</span>
                    <span class="badge ${ok ? "badge-success" : "badge-danger"}">${ok ? "Correct" : "Incorrect"}</span>
                  </div>
                  <p style="font-weight:600; color:var(--ink-primary); margin-bottom:0.45rem;">${renderInlineMd(q.question)}</p>
                  <p style="font-size:0.84rem; margin-bottom:0.35rem;">
                    <strong>Your answer:</strong> ${sel !== undefined ? `${LETTERS[sel]}. ${renderInlineMd(q.options[sel])}` : "Unanswered"}<br />
                    <strong>Correct answer:</strong> ${LETTERS[q.correct_index]}. ${renderInlineMd(q.options[q.correct_index])}
                  </p>
                  <p style="font-size:0.84rem; color:var(--ink-secondary);">${renderInlineMd(q.explanation)}</p>
                </div>
              `;
            })
            .join("")}
        </div>
      </div>
    `;

    container.querySelector("#retake-exam-btn").addEventListener("click", () => startSession(mode, studyDomain));
    container.querySelector("#back-launcher-btn").addEventListener("click", () => {
      phase = "launcher";
      render();
    });
  }

  render();
}
