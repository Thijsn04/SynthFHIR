/* SynthFHIR web console.
   Vanilla JS, no build step. Talks to the SynthFHIR REST API on the same origin. */

"use strict";

const MAX_HIGHLIGHT_BYTES = 600 * 1024; // skip syntax highlight above this to stay responsive
const MAX_RESOURCE_ITEMS = 400;         // cap rendered entries in the Resources tab

const state = {
  segments: { version: "R4", format: "bundle", bundle_type: "collection", profile: "base" },
  lastText: null,
  lastFormat: "bundle",
};

const $ = (id) => document.getElementById(id);

/* ---------------------------------------------------------------- base URL */
function apiBase() {
  const manual = $("baseUrl").value.trim().replace(/\/+$/, "");
  if (manual) return manual;
  if (location.protocol === "http:" || location.protocol === "https:") return location.origin;
  return "http://localhost:8000";
}

/* ------------------------------------------------------------------- theme */
function initTheme() {
  const saved = localStorage.getItem("synthfhir-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  $("themeToggle").addEventListener("click", () => {
    const current =
      document.documentElement.getAttribute("data-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("synthfhir-theme", next);
  });
}

/* --------------------------------------------------------- segmented state */
function initSegments() {
  document.querySelectorAll(".segmented").forEach((group) => {
    const field = group.dataset.field;
    group.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        group.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
        btn.setAttribute("aria-pressed", "true");
        state.segments[field] = btn.dataset.value;
      });
    });
  });
}

/* ------------------------------------------------------------- conditions */
async function loadConditions() {
  try {
    const res = await fetch(apiBase() + "/api/conditions", { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return;
    const items = await res.json();
    const sel = $("condition");
    items
      .sort((a, b) => a.display.localeCompare(b.display))
      .forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.key;
        opt.textContent = c.display;
        sel.appendChild(opt);
      });
  } catch {
    /* offline; the Any-condition default still works */
  }
}

/* ----------------------------------------------------------- server health */
async function checkHealth() {
  const dot = $("statusDot");
  const label = $("statusLabel");
  dot.className = "dot checking";
  label.textContent = "checking";
  try {
    const t0 = performance.now();
    const res = await fetch(apiBase() + "/health", { signal: AbortSignal.timeout(3000) });
    const ms = Math.round(performance.now() - t0);
    if (res.ok) {
      dot.className = "dot online";
      label.textContent = `online, ${ms} ms`;
    } else {
      dot.className = "dot offline";
      label.textContent = `error ${res.status}`;
    }
  } catch {
    dot.className = "dot offline";
    label.textContent = "offline";
  }
}

/* --------------------------------------------------------------- URL build */
function buildUrl() {
  const params = new URLSearchParams();
  const num = (id) => {
    const v = $(id).value.trim();
    if (v !== "") params.set(id, v);
  };
  num("count");
  params.set("version", state.segments.version);
  num("age_min");
  num("age_max");
  const cond = $("condition").value;
  if (cond) params.set("condition", cond);
  num("years");
  num("num_practitioners");
  num("num_organizations");
  params.set("bundle_type", state.segments.bundle_type);
  params.set("format", state.segments.format);
  params.set("profile", state.segments.profile);
  num("seed");
  return apiBase() + "/api/generate/cohort?" + params.toString();
}

/* --------------------------------------------------------------- generate */
async function generate(event) {
  event.preventDefault();

  const btn = $("generateBtn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spin"></span> Generating';
  $("statusPill").className = "pill";
  $("statusPill").textContent = "Running";
  $("errBox").hidden = true;

  const url = buildUrl();
  const t0 = performance.now();

  try {
    const res = await fetch(url);
    const text = await res.text();
    const ms = Math.round(performance.now() - t0);
    const bytes = new TextEncoder().encode(text).length;
    const isNdjson =
      state.segments.format === "ndjson" ||
      (res.headers.get("content-type") || "").includes("ndjson");

    state.lastText = text;
    state.lastFormat = isNdjson ? "ndjson" : "bundle";

    const pill = $("statusPill");
    pill.className = "pill " + (res.ok ? "ok" : "err");
    pill.textContent = `${res.status} ${res.statusText}`;

    if (!res.ok) {
      showError(text);
      resetMetrics(ms, bytes, 0);
      return;
    }

    const counts = tallyResources(text, isNdjson);
    const total = Object.values(counts).reduce((a, b) => a + b, 0);

    renderSummary(counts, total);
    renderPreview(text, bytes);
    renderResources(text, isNdjson);
    revealResult(ms, bytes, total);
  } catch (err) {
    $("statusPill").className = "pill err";
    $("statusPill").textContent = "Network error";
    showError(String(err && err.message ? err.message : err));
    checkHealth();
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate";
  }
}

function resetMetrics(ms, bytes, total) {
  $("mTime").textContent = ms;
  $("mSize").textContent = (bytes / 1024).toFixed(1);
  $("mCount").textContent = total;
  $("metrics").hidden = false;
}

function revealResult(ms, bytes, total) {
  resetMetrics(ms, bytes, total);
  $("emptyState").hidden = true;
  $("tabs").hidden = false;
  $("copyBtn").hidden = false;
  $("downloadBtn").hidden = false;
  selectTab("summary");
}

/* --------------------------------------------------------------- tallying */
function tallyResources(text, isNdjson) {
  const counts = {};
  const bump = (t) => {
    if (!t) return;
    counts[t] = (counts[t] || 0) + 1;
  };
  if (isNdjson) {
    text.split("\n").forEach((line) => {
      const s = line.trim();
      if (!s) return;
      try {
        bump(JSON.parse(s).resourceType);
      } catch {
        /* skip malformed line */
      }
    });
  } else {
    try {
      const bundle = JSON.parse(text);
      (bundle.entry || []).forEach((e) => bump(e.resource && e.resource.resourceType));
    } catch {
      /* not a bundle */
    }
  }
  return counts;
}

/* --------------------------------------------------------------- rendering */
function renderSummary(counts, total) {
  $("totalCount").textContent = total.toLocaleString();
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  $("typeCount").textContent = entries.length;
  const max = entries.length ? entries[0][1] : 1;
  const table = $("rtable");
  table.innerHTML = "";
  entries.forEach(([type, n]) => {
    const row = document.createElement("div");
    row.className = "rrow";
    const pct = Math.max(4, Math.round((n / max) * 120));
    row.innerHTML =
      `<div class="rt"><span>${escapeHtml(type)}</span>` +
      `<span class="bar" style="width:${pct}px"></span></div>` +
      `<span class="rc">${n.toLocaleString()}</span>`;
    table.appendChild(row);
  });
}

function renderPreview(text, bytes) {
  const el = $("previewCode");
  let pretty = text;
  if (state.lastFormat === "bundle") {
    try {
      pretty = JSON.stringify(JSON.parse(text), null, 2);
    } catch {
      /* leave as-is */
    }
  }
  if (bytes <= MAX_HIGHLIGHT_BYTES) {
    el.innerHTML = highlightJson(pretty);
  } else {
    el.textContent = pretty;
  }
}

function renderResources(text, isNdjson) {
  const list = $("rlist");
  list.innerHTML = "";
  let resources = [];
  if (isNdjson) {
    resources = text
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean)
      .map(safeParse);
  } else {
    try {
      resources = (JSON.parse(text).entry || []).map((e) => e.resource);
    } catch {
      resources = [];
    }
  }
  const shown = resources.slice(0, MAX_RESOURCE_ITEMS);
  shown.forEach((r, i) => {
    const item = document.createElement("details");
    item.className = "ritem";
    const type = (r && r.resourceType) || "unknown";
    const rid = (r && r.id) || "";
    item.innerHTML =
      `<summary><span class="idx">#${i + 1}</span>` +
      `<span class="type">${escapeHtml(type)}</span>` +
      `<span class="rid">${escapeHtml(rid)}</span></summary>` +
      `<pre class="code">${highlightJson(JSON.stringify(r, null, 2))}</pre>`;
    list.appendChild(item);
  });
  if (resources.length > shown.length) {
    const note = document.createElement("div");
    note.className = "empty";
    note.style.padding = "18px";
    note.innerHTML = `<div class="s">Showing first ${shown.length} of ${resources.length} resources. Download for the full set.</div>`;
    list.appendChild(note);
  }
}

function showError(text) {
  let detail = text;
  try {
    detail = JSON.stringify(JSON.parse(text).detail || JSON.parse(text), null, 2);
  } catch {
    /* raw text */
  }
  const box = $("errBox");
  box.hidden = false;
  box.innerHTML =
    `<div class="h">Request failed</div>` +
    `<div class="m">${escapeHtml(detail)}</div>` +
    `<div class="s">Confirm SynthFHIR is running at <code>${escapeHtml(apiBase())}</code>.</div>`;
  $("emptyState").hidden = true;
  $("tabs").hidden = true;
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
}

/* ------------------------------------------------------------------- tabs */
function selectTab(name) {
  document.querySelectorAll(".tab").forEach((t) =>
    t.setAttribute("aria-selected", String(t.dataset.tab === name))
  );
  document.querySelectorAll(".panel").forEach((p) =>
    p.classList.toggle("active", p.id === "panel-" + name)
  );
  $("errBox").hidden = true;
}

/* --------------------------------------------------------- copy / download */
function copyResult() {
  if (!state.lastText) return;
  navigator.clipboard.writeText(state.lastText).then(() => flash($("copyBtn"), "Copied"));
}

function downloadResult() {
  if (!state.lastText) return;
  const ndjson = state.lastFormat === "ndjson";
  const blob = new Blob([state.lastText], {
    type: ndjson ? "application/fhir+ndjson" : "application/fhir+json",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `synthfhir-cohort.${ndjson ? "ndjson" : "json"}`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function flash(btn, msg) {
  const original = btn.textContent;
  btn.textContent = msg;
  setTimeout(() => (btn.textContent = original), 1400);
}

/* ---------------------------------------------------------------- helpers */
function safeParse(s) {
  try {
    return JSON.parse(s);
  } catch {
    return { resourceType: "unparsed", raw: s };
  }
}

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function highlightJson(json) {
  const escaped = escapeHtml(json);
  return escaped.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|\bnull\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = "tok-num";
      if (/^"/.test(match)) cls = /:$/.test(match) ? "tok-key" : "tok-str";
      else if (/true|false/.test(match)) cls = "tok-bool";
      else if (/null/.test(match)) cls = "tok-null";
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

function resetForm() {
  $("count").value = 10;
  $("age_min").value = 0;
  $("age_max").value = 80;
  $("condition").value = "";
  $("years").value = 2;
  $("num_practitioners").value = 3;
  $("num_organizations").value = 1;
  $("seed").value = "";
  const defaults = { version: "R4", format: "bundle", bundle_type: "collection", profile: "base" };
  Object.entries(defaults).forEach(([field, value]) => {
    state.segments[field] = value;
    const group = document.querySelector(`.segmented[data-field="${field}"]`);
    if (!group) return;
    group.querySelectorAll("button").forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.value === value))
    );
  });
}

/* ------------------------------------------------------------------- init */
function init() {
  initTheme();
  initSegments();
  loadConditions();
  checkHealth();

  $("configCard").addEventListener("submit", generate);
  $("resetBtn").addEventListener("click", resetForm);
  $("copyBtn").addEventListener("click", copyResult);
  $("downloadBtn").addEventListener("click", downloadResult);
  $("baseUrl").addEventListener("change", checkHealth);
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => selectTab(t.dataset.tab))
  );
}

document.addEventListener("DOMContentLoaded", init);
