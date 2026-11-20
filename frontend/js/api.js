/**
 * API client for AI-901 Study Studio FastAPI backend.
 */

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const errBody = await res.json();
      if (errBody?.detail) {
        detail = typeof errBody.detail === "string"
          ? errBody.detail
          : JSON.stringify(errBody.detail);
      }
    } catch {
      // ignore non-JSON body
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  getStatus: () => request("/api/status"),
  getCurriculum: () => request("/api/curriculum"),
  askStudyCoach: (payload) =>
    request("/api/study-coach", { method: "POST", body: JSON.stringify(payload) }),
  runFoundryChat: (payload) =>
    request("/api/labs/chat", { method: "POST", body: JSON.stringify(payload) }),
  runFoundryAgent: (payload) =>
    request("/api/labs/agent", { method: "POST", body: JSON.stringify(payload) }),
  runTextAnalysis: (payload) =>
    request("/api/labs/text-analysis", { method: "POST", body: JSON.stringify(payload) }),
  runSpeechLab: (payload) =>
    request("/api/labs/speech", { method: "POST", body: JSON.stringify(payload) }),
  runContentUnderstanding: (payload) =>
    request("/api/labs/content-understanding", { method: "POST", body: JSON.stringify(payload) }),
  runVisionLab: (payload) =>
    request("/api/labs/vision", { method: "POST", body: JSON.stringify(payload) }),
};
