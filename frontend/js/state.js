/**
 * Persistent study progress state stored in localStorage.
 */

const STORAGE_KEY = "ai901_study_studio_state_v1";

const DEFAULT_STATE = {
  completedModules: [],
  flashcardRatings: {}, // { [cardId]: "review" | "familiar" | "mastered" }
  examHistory: [],      // [{ date, mode, scaledScore, correct, total, passed, domainScores }]
};

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return structuredClone(DEFAULT_STATE);
    const parsed = JSON.parse(raw);
    return {
      completedModules: Array.isArray(parsed.completedModules) ? parsed.completedModules : [],
      flashcardRatings: parsed.flashcardRatings && typeof parsed.flashcardRatings === "object"
        ? parsed.flashcardRatings
        : {},
      examHistory: Array.isArray(parsed.examHistory) ? parsed.examHistory : [],
    };
  } catch {
    return structuredClone(DEFAULT_STATE);
  }
}

let state = loadState();
const listeners = new Set();

function save() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // ignore storage quota failures
  }
  listeners.forEach((fn) => fn(state));
}

export const studyState = {
  get: () => state,

  subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },

  toggleModuleComplete(moduleId) {
    const idx = state.completedModules.indexOf(moduleId);
    if (idx >= 0) {
      state.completedModules.splice(idx, 1);
    } else {
      state.completedModules.push(moduleId);
    }
    save();
  },

  isModuleComplete(moduleId) {
    return state.completedModules.includes(moduleId);
  },

  setFlashcardRating(cardId, rating) {
    state.flashcardRatings[cardId] = rating;
    save();
  },

  getFlashcardRating(cardId) {
    return state.flashcardRatings[cardId] || null;
  },

  recordExamAttempt(attempt) {
    state.examHistory.unshift(attempt);
    if (state.examHistory.length > 12) {
      state.examHistory = state.examHistory.slice(0, 12);
    }
    save();
  },

  computeReadiness(curriculum) {
    if (!curriculum) return 0;
    const totalModules = curriculum.modules.length || 1;
    const modRatio = state.completedModules.length / totalModules;

    const totalCards = curriculum.flashcards.length || 1;
    let cardPoints = 0;
    for (const card of curriculum.flashcards) {
      const r = state.flashcardRatings[card.id];
      if (r === "mastered") cardPoints += 1;
      else if (r === "familiar") cardPoints += 0.5;
    }
    const cardRatio = cardPoints / totalCards;

    let bestExamRatio = 0;
    if (state.examHistory.length > 0) {
      const bestScore = Math.max(...state.examHistory.map((h) => h.scaledScore || 0));
      bestExamRatio = Math.min(1, bestScore / 1000);
    }

    // Weighted readiness: 35% guides, 30% flashcards, 35% practice exam
    return Math.round((modRatio * 0.35 + cardRatio * 0.3 + bestExamRatio * 0.35) * 100);
  },
};
