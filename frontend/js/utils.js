/**
 * Shared UI utilities for AI-901 Study Studio.
 */

export function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * Safely render lightweight inline markdown (**bold** and `code`) after HTML escaping.
 */
export function renderInlineMd(text) {
  const safe = escapeHtml(text);
  return safe
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

let toastTimer = null;
export function showToast(message) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  el.classList.remove("is-hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.add("is-hidden");
  }, 2400);
}

export async function copyToClipboard(text, label = "Copied to clipboard") {
  try {
    await navigator.clipboard.writeText(text);
    showToast(label);
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    document.body.removeChild(area);
    showToast(label);
  }
}

export function domainBadge(domainId) {
  if (domainId === "domain-1") {
    return `<span class="badge badge-domain-1">Domain 1 · Concepts</span>`;
  }
  return `<span class="badge badge-domain-2">Domain 2 · Foundry</span>`;
}
