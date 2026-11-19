/* EduExplained analytics layer → Google Analytics 4 through gtag(). Loaded by Base.astro only when a measurement id is
   configured and the build is production (or SITE_ANALYTICS_PREVIEW=1). Consent Mode v2 starts denied; this script
   upgrades it after the reader's choice in the consent bar and reports every meaningful interaction.
   Parameters are page identifiers and counts only: never an email, a search query, feedback text, a name or a location. */
(function () {
  "use strict";
  if (typeof window.gtag !== "function") { window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); }; }
  var d = document.body.dataset;
  var COMMON = { page_path: location.pathname, page_type: d.pageType || "", school: d.school || "", topic: d.topic || "", author: d.author || "",
                 words: d.words ? Number(d.words) : undefined, indexed: d.indexed || "", device_class: deviceClass(), environment: d.environment || "" };
  var SENT = Object.create(null), seen = {};
  function deviceClass() { var w = window.innerWidth || 0; return w < 600 ? "phone" : (w < 1024 ? "tablet" : "desktop"); }
  function cookie(n) { var m = document.cookie.match(new RegExp("(?:^|; )" + n + "=([^;]*)")); return m ? decodeURIComponent(m[1]) : ""; }
  function consent() { return cookie("ee_consent"); } // "" | none | analytics | all
  function analyticsOk() { var c = consent(); return c === "analytics" || c === "all"; }
  function adsOk() { return consent() === "all"; }
  function applyConsent() {
    window.gtag("consent", "update", { analytics_storage: analyticsOk() ? "granted" : "denied", ad_storage: adsOk() ? "granted" : "denied",
      ad_user_data: adsOk() ? "granted" : "denied", ad_personalization: adsOk() ? "granted" : "denied" });
  }
  function track(name, params, once) {
    if (once) { if (SENT[once]) return; SENT[once] = true; }
    var p = {}; for (var k in COMMON) if (COMMON[k] !== undefined && COMMON[k] !== "") p[k] = COMMON[k];
    for (var j in (params || {})) { var v = params[j]; if (v === undefined || v === null || v === "") continue; if (typeof v === "string" && v.length > 100) v = v.slice(0, 100); p[j] = v; }
    if (d.tagKind === "gtm") { var o = { event: name }; for (var q in p) o[q] = p[q]; window.dataLayer.push(o); }
    else window.gtag("event", name, p);
  }
  window.EEAnalytics = { track: track, applyConsent: applyConsent };
  applyConsent();

  /* consent bar */
  var bar = document.querySelector("[data-consent]");
  if (bar) {
    if (consent()) bar.remove();
    bar.querySelectorAll("[data-consent-choice]").forEach(function (b) {
      b.addEventListener("click", function () {
        var val = b.getAttribute("data-consent-choice");
        document.cookie = "ee_consent=" + val + ";path=/;max-age=15552000;SameSite=Lax" + (location.protocol === "https:" ? ";Secure" : "");
        applyConsent(); track("consent_choice", { choice: val }); bar.remove();
      });
    });
  }
  document.querySelectorAll("[data-consent-open]").forEach(function (el) {
    el.addEventListener("click", function (e) { e.preventDefault(); document.cookie = "ee_consent=;path=/;max-age=0"; location.reload(); });
  });

  /* page view, once per load */
  track("page_view", { page_location: location.origin + location.pathname, page_title: document.title, sources: document.querySelectorAll(".sources__item").length,
    has_tool: !!document.querySelector(".tool-embed"), has_facts: !!document.querySelector(".facts, table.facts"), lead_photo: !!document.querySelector(".lead-photo, figure.lead") }, "page_view");
  if (d.pageType === "not_found") track("error_404", { path: location.pathname, referrer_host: refHost() }, "error_404");
  function refHost() { try { return document.referrer ? new URL(document.referrer).hostname : ""; } catch (_) { return ""; } }

  /* scroll depth, reading time, exit */
  var marks = [25, 50, 75, 100];
  function onScroll() { var h = document.documentElement, max = h.scrollHeight - h.clientHeight; if (max <= 0) return; var pct = Math.round((h.scrollTop || window.pageYOffset) / max * 100);
    marks.forEach(function (m) { if (pct >= m && !seen[m]) { seen[m] = true; track("scroll_depth", { percent: m }); } }); }
  window.addEventListener("scroll", throttle(onScroll, 400), { passive: true }); onScroll();
  var engaged = 0, last = Date.now(), visible = !document.hidden;
  document.addEventListener("visibilitychange", function () { var n = Date.now(); if (visible) engaged += n - last; visible = !document.hidden; last = n; });
  setInterval(function () { if (visible) { engaged += Date.now() - last; last = Date.now(); } [15, 60, 180, 420].forEach(function (s) { if (engaged >= s * 1000 && !seen["t" + s]) { seen["t" + s] = true; track("engaged_time", { seconds: s }); } }); }, 5000);
  window.addEventListener("pagehide", function () { var m = 0; marks.forEach(function (x) { if (seen[x]) m = x; }); track("page_exit", { engaged_seconds: Math.round(engaged / 1000), max_scroll: m }); });

  /* sections and FAQ reached (IntersectionObserver) */
  try {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; var el = e.target; io.unobserve(el);
      if (el.matches(".faq")) track("faq_view", { items: el.querySelectorAll(".faq__item").length }, "faq_view");
      else if (el.matches(".sources")) track("sources_view", { count: el.querySelectorAll(".sources__item").length }, "sources_view");
      else if (el.matches(".related")) track("related_view", { count: el.querySelectorAll("a").length }, "related_view");
      else if (el.matches(".feedback")) track("feedback_view", {}, "feedback_view");
      else if (el.matches(".tool-embed")) track("tool_view", {}, "tool_view");
      else if (el.matches("h2[id]")) track("section_view", { section_id: el.id, section: (el.textContent || "").trim().slice(0, 60) });
    }); }, { threshold: 0.25 });
    document.querySelectorAll(".faq, .sources, .related, .feedback, .tool-embed, article .prose h2[id], .section h2[id]").forEach(function (el) { io.observe(el); });
  } catch (_) {}

  /* every click, classified by where it happened */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a, button, summary"); if (!a) return;
    var txt = (a.textContent || "").trim().slice(0, 80);
    if (a.tagName === "A") {
      var url; try { url = new URL(a.href, location.href); } catch (_) { return; }
      var external = url.origin !== location.origin;
      var section = a.closest(".sources") ? "sources" : a.closest(".fn") ? "footnote" : a.closest(".toc") ? "toc" : a.closest(".related") ? "related" : a.closest(".crumbs") ? "breadcrumbs"
        : a.closest(".masthead") ? "masthead" : a.closest(".subnav, .school-subnav") ? "subnav" : a.closest("footer") ? "footer" : a.closest(".sidebar, aside") ? "sidebar" : a.closest(".card") ? "card"
        : a.closest(".prose, .article-sections, .short-answer") ? "body_text" : a.closest(".tool-embed") ? "tool" : a.closest(".hub, .guide-list") ? "hub_list" : a.closest(".skip") ? "skip_link" : "other";
      var ev = section === "sources" ? "source_click" : section === "footnote" ? "footnote_click" : section === "toc" ? "toc_click" : section === "related" ? "related_link_click"
        : section === "breadcrumbs" ? "breadcrumb_click" : (section === "masthead" || section === "subnav" || section === "footer") ? "nav_click"
        : /\.csv(\?|$)/.test(url.pathname) ? "file_download" : external ? "outbound_click" : "internal_link_click";
      track(ev, { link_text: txt, link_url: external ? url.origin + url.pathname : url.pathname + (url.hash || ""), section: section, outbound: external, link_host: external ? url.hostname : undefined });
    } else if (!a.hasAttribute("data-consent-choice")) {
      var form = a.closest("form");
      track("button_click", { button_text: txt, section: form ? (form.classList.contains("feedback__form") ? "feedback" : form.classList.contains("newsletter__form") ? "newsletter" : form.classList.contains("search") ? "search" : form.closest(".tool-embed") ? "tool" : "form") : (a.closest(".tool-embed") ? "tool" : "page") });
    }
  }, true);

  /* forms: counts and choices only, never the text */
  document.addEventListener("submit", function (e) {
    var f = e.target; if (!(f instanceof HTMLFormElement)) return;
    if (f.classList.contains("feedback__form")) { var sub = e.submitter; var ans = sub && sub.name === "answered" ? sub.value : (f.querySelector("[name=need]") && f.querySelector("[name=need]").value ? "no" : "yes"); track("feedback_submit", { answered: ans, need_length: (f.querySelector("[name=need]") || {}).value ? f.querySelector("[name=need]").value.length : 0 }); }
    else if (f.classList.contains("newsletter__form")) track("newsletter_submit", { placement: f.closest(".newsletter--side") ? "sidebar" : (f.closest(".newsletter--wide") ? "wide" : "inline") });
    else if (f.classList.contains("search")) { var q = f.querySelector("input[type=search]"); track("search_submit", { query_length: q && q.value ? q.value.trim().length : 0 }); }
    else if (f.closest(".tool-embed")) track("tool_submit", { tool_form: f.id || f.getAttribute("name") || "" });
    else track("form_submit", { form: f.getAttribute("name") || f.id || "" });
  }, true);

  /* tools: first touch, then each input (field name only) */
  document.querySelectorAll(".tool-embed").forEach(function (t) {
    var started = false;
    t.addEventListener("input", function (e) { var el = e.target; if (!started) { started = true; track("tool_start", {}, "tool_start"); }
      track("tool_input", { field: el.name || el.id || el.type || "", kind: el.tagName.toLowerCase() === "select" ? "select" : (el.type || "input") }); });
    t.addEventListener("change", function (e) { var el = e.target; if (el.tagName === "SELECT" || el.type === "checkbox" || el.type === "radio") track("tool_change", { field: el.name || el.id || "", value_kind: el.type || "select" }); });
  });
  if (document.querySelector(".tool-embed") && window.MutationObserver) {
    var completeSent = false; var mo = new MutationObserver(function () { if (!completeSent && document.querySelector(".tool-embed [data-result], .tool-embed output, .tool-embed .result")) { completeSent = true; track("tool_complete", {}, "tool_complete"); } });
    mo.observe(document.querySelector(".tool-embed"), { childList: true, subtree: true, characterData: true });
  }

  /* search results page (Pagefind) */
  if (d.pageType === "search") {
    var t0 = Date.now(); var iv = setInterval(function () { var n = document.querySelectorAll(".pagefind-ui__result").length; var msg = document.querySelector(".pagefind-ui__message");
      if (n || (msg && /no results/i.test(msg.textContent)) || Date.now() - t0 > 8000) { clearInterval(iv); track("search_results", { result_count: n, empty: n === 0 }, "search_results"); } }, 500);
  }

  /* data tables and charts */
  document.querySelectorAll("table").forEach(function (tb, i) { try { var io2 = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { io2.disconnect(); track("table_view", { rows: tb.querySelectorAll("tbody tr").length, index: i }); } }); }, { threshold: 0.3 }); io2.observe(tb); } catch (_) {} });

  /* copy, print, share-ish */
  document.addEventListener("copy", function () { var s = String(window.getSelection() || ""); track("text_copy", { length: s.length }); });
  window.addEventListener("beforeprint", function () { track("print", {}, "print"); });

  /* web vitals */
  try {
    var lcp = 0, cls = 0, inp = 0;
    new PerformanceObserver(function (l) { var es = l.getEntries(); lcp = es[es.length - 1].startTime; }).observe({ type: "largest-contentful-paint", buffered: true });
    new PerformanceObserver(function (l) { l.getEntries().forEach(function (e) { if (!e.hadRecentInput) cls += e.value; }); }).observe({ type: "layout-shift", buffered: true });
    new PerformanceObserver(function (l) { l.getEntries().forEach(function (e) { if (e.duration > inp) inp = e.duration; }); }).observe({ type: "event", buffered: true, durationThreshold: 40 });
    var nav = performance.getEntriesByType("navigation")[0], fcp = performance.getEntriesByName("first-contentful-paint")[0];
    window.addEventListener("pagehide", function () { track("web_vitals", { lcp_ms: Math.round(lcp), cls: Math.round(cls * 1000) / 1000, inp_ms: Math.round(inp), fcp_ms: fcp ? Math.round(fcp.startTime) : undefined, ttfb_ms: nav ? Math.round(nav.responseStart) : undefined }, "web_vitals"); });
  } catch (_) {}
  window.addEventListener("error", function (e) { track("js_error", { message: String(e.message || "").slice(0, 100), source: (e.filename || "").split("/").pop() }); });
  function throttle(fn, ms) { var t = 0; return function () { var n = Date.now(); if (n - t > ms) { t = n; fn(); } }; }
})();
