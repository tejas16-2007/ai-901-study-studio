/**
 * View 2: Spaced-Repetition Flashcards for Exam AI-901 (32 cards).
 */

import { studyState } from "../state.js";
import { domainBadge, escapeHtml, renderInlineMd, showToast } from "../utils.js";

export function renderFlashcardsView(container, curriculum) {
  let domainFilter = "all";
  let statusFilter = "all";
  let deck = [...curriculum.flashcards];
  let index = 0;
  let flipped = false;

  function filteredDeck() {
    const ratings = studyState.get().flashcardRatings;
    return deck.filter((card) => {
      if (domainFilter !== "all" && card.domain_id !== domainFilter) return false;
      const r = ratings[card.id] || "unseen";
      if (statusFilter === "review" && r !== "review") return false;
      if (statusFilter === "unseen" && r !== "unseen") return false;
      if (statusFilter === "mastered" && r !== "mastered") return false;
      return true;
    });
  }

  function shuffleDeck() {
    for (let i = deck.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    index = 0;
    flipped = false;
    showToast("Deck shuffled");
    render();
  }

  function rateCurrent(rating) {
    const cards = filteredDeck();
    if (!cards.length) return;
    const card = cards[index % cards.length];
    studyState.setFlashcardRating(card.id, rating);
    flipped = false;
    if (index < cards.length - 1) {
      index += 1;
    } else {
      index = 0;
    }
    render();
  }

  function render() {
    const cards = filteredDeck();
    if (index >= cards.length) index = 0;
    const current = cards[index];

    const ratings = studyState.get().flashcardRatings;
    const masteredCount = curriculum.flashcards.filter((c) => ratings[c.id] === "mastered").length;
    const reviewCount = curriculum.flashcards.filter((c) => ratings[c.id] === "review").length;
    const currentRating = current ? ratings[current.id] : null;

    container.innerHTML = `
      <div class="page-intro">
        <div>
          <h1 id="flashcards-heading">AI-901 Active Recall Flashcards</h1>
          <p class="page-lead">
            Flip cards with <code>Space</code>, navigate with <code>←</code> / <code>→</code>, and rate confidence with <code>1</code> (Review), <code>2</code> (Familiar), or <code>3</code> (Mastered).
          </p>
        </div>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <span class="badge badge-success">${masteredCount} / ${curriculum.flashcards.length} mastered</span>
          <span class="badge badge-danger">${reviewCount} needs review</span>
        </div>
      </div>

      <div class="fc-toolbar surface-card" style="padding:0.9rem 1.15rem;">
        <div class="fc-filters">
          <button class="chip-btn ${domainFilter === "all" ? "is-active" : ""}" data-fc-domain="all" type="button">All Domains (${curriculum.flashcards.length})</button>
          <button class="chip-btn ${domainFilter === "domain-1" ? "is-active" : ""}" data-fc-domain="domain-1" type="button">Domain 1 · Concepts</button>
          <button class="chip-btn ${domainFilter === "domain-2" ? "is-active" : ""}" data-fc-domain="domain-2" type="button">Domain 2 · Foundry</button>
        </div>
        <div class="fc-filters">
          <select class="field-select" id="fc-status-select" style="width:auto; padding:0.38rem 0.65rem; font-size:0.82rem;" aria-label="Filter by mastery status">
            <option value="all" ${statusFilter === "all" ? "selected" : ""}>All statuses</option>
            <option value="unseen" ${statusFilter === "unseen" ? "selected" : ""}>Unseen only</option>
            <option value="review" ${statusFilter === "review" ? "selected" : ""}>Needs review</option>
            <option value="mastered" ${statusFilter === "mastered" ? "selected" : ""}>Mastered</option>
          </select>
          <button class="btn btn-secondary btn-sm" id="fc-shuffle-btn" type="button">Shuffle</button>
        </div>
      </div>

      <div class="fc-stage">
        ${
          !current
            ? `
              <div class="surface-card" style="text-align:center; padding:3rem 1.5rem;">
                <h2 style="margin-bottom:0.4rem;">No cards match this filter</h2>
                <p style="color:var(--ink-muted); margin-bottom:1rem;">Switch back to "All statuses" to keep drilling the deck.</p>
                <button class="btn btn-primary btn-sm" id="fc-reset-filters" type="button">Reset Filters</button>
              </div>
            `
            : `
              <div class="fc-progress-bar">
                <span>Card <strong>${index + 1}</strong> of <strong>${cards.length}</strong></span>
                <div class="bar-track" style="flex:1; max-width:340px;">
                  <div class="bar-fill" style="width:${Math.round(((index + 1) / cards.length) * 100)}%"></div>
                </div>
                <span class="eyebrow">${escapeHtml(current.tag)}</span>
              </div>

              <div class="fc-card-wrap">
                <div class="fc-card ${flipped ? "is-flipped" : ""}" id="fc-flip-card" role="button" tabindex="0" aria-label="Flip flashcard">
                  <div class="fc-face fc-front">
                    <div class="fc-face-top">
                      ${domainBadge(current.domain_id)}
                      <span class="badge badge-neutral">${escapeHtml(current.tag)}</span>
                    </div>
                    <div class="fc-prompt">${renderInlineMd(current.front)}</div>
                    <div class="fc-hint">
                      <span>Click card or press <code>Space</code> to reveal answer</span>
                      ${
                        currentRating
                          ? `<span class="badge badge-${currentRating === "mastered" ? "success" : currentRating === "familiar" ? "warn" : "danger"}">${escapeHtml(currentRating)}</span>`
                          : `<span>Unrated</span>`
                      }
                    </div>
                  </div>
                  <div class="fc-face fc-back">
                    <div class="fc-face-top">
                      <span class="badge badge-success">Answer</span>
                      <span class="badge badge-neutral">${escapeHtml(current.tag)}</span>
                    </div>
                    <div class="fc-answer">${renderInlineMd(current.back)}</div>
                    <div class="fc-hint">
                      <span>Rate how well you knew this below</span>
                      <span>Click to flip back</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="fc-controls">
                <div style="display:flex; gap:0.5rem;">
                  <button class="btn btn-secondary btn-sm" id="fc-prev-btn" type="button">← Previous</button>
                  <button class="btn btn-secondary btn-sm" id="fc-next-btn" type="button">Next →</button>
                </div>
                <div class="fc-ratings">
                  <button class="rate-btn rate-review ${currentRating === "review" ? "is-selected" : ""}" data-rate="review" type="button">1 · Needs Review</button>
                  <button class="rate-btn rate-familiar ${currentRating === "familiar" ? "is-selected" : ""}" data-rate="familiar" type="button">2 · Familiar</button>
                  <button class="rate-btn rate-mastered ${currentRating === "mastered" ? "is-selected" : ""}" data-rate="mastered" type="button">3 · Mastered</button>
                </div>
              </div>
            `
        }
      </div>
    `;

    bindEvents(cards);
  }

  function bindEvents(cards) {
    container.querySelectorAll("[data-fc-domain]").forEach((btn) => {
      btn.addEventListener("click", () => {
        domainFilter = btn.dataset.fcDomain;
        index = 0;
        flipped = false;
        render();
      });
    });

    const statusSel = container.querySelector("#fc-status-select");
    if (statusSel) {
      statusSel.addEventListener("change", () => {
        statusFilter = statusSel.value;
        index = 0;
        flipped = false;
        render();
      });
    }

    const shuffleBtn = container.querySelector("#fc-shuffle-btn");
    if (shuffleBtn) shuffleBtn.addEventListener("click", shuffleDeck);

    const resetBtn = container.querySelector("#fc-reset-filters");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        domainFilter = "all";
        statusFilter = "all";
        index = 0;
        flipped = false;
        render();
      });
    }

    const cardEl = container.querySelector("#fc-flip-card");
    if (cardEl) {
      cardEl.addEventListener("click", () => {
        flipped = !flipped;
        cardEl.classList.toggle("is-flipped", flipped);
      });
    }

    const prevBtn = container.querySelector("#fc-prev-btn");
    const nextBtn = container.querySelector("#fc-next-btn");
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (!cards.length) return;
        index = (index - 1 + cards.length) % cards.length;
        flipped = false;
        render();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (!cards.length) return;
        index = (index + 1) % cards.length;
        flipped = false;
        render();
      });
    }

    container.querySelectorAll("[data-rate]").forEach((btn) => {
      btn.addEventListener("click", () => rateCurrent(btn.dataset.rate));
    });
  }

  // Keyboard shortcuts active only when flashcards view is visible
  const onKeyDown = (e) => {
    if (container.classList.contains("is-hidden")) return;
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
    const cards = filteredDeck();
    if (!cards.length) return;

    if (e.code === "Space") {
      e.preventDefault();
      flipped = !flipped;
      const cardEl = container.querySelector("#fc-flip-card");
      if (cardEl) cardEl.classList.toggle("is-flipped", flipped);
    } else if (e.key === "ArrowRight") {
      index = (index + 1) % cards.length;
      flipped = false;
      render();
    } else if (e.key === "ArrowLeft") {
      index = (index - 1 + cards.length) % cards.length;
      flipped = false;
      render();
    } else if (e.key === "1") {
      rateCurrent("review");
    } else if (e.key === "2") {
      rateCurrent("familiar");
    } else if (e.key === "3") {
      rateCurrent("mastered");
    }
  };

  window.addEventListener("keydown", onKeyDown);
  render();
}
