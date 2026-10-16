/* Hot Rod History: small progressive enhancements. Everything here is optional; the site is complete without JS.
   - Contents (garage-sign index) panel
   - reading-progress bar, "in this story" scroll-spy
   - header link current-state (header persists under instant navigation)
   - filter box for long tables
   - fallback chip for legacy record boxes that the build hook could not parse */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- contents panel ---- */
  function panel() { return $("#hr-contents"); }
  function setContents(open) {
    var p = panel(); if (!p) return;
    p.hidden = !open;
    $$("[data-hr-contents-toggle]").forEach(function (b) { if (b.tagName === "BUTTON" && b.classList.contains("hr-bar__contents")) b.setAttribute("aria-expanded", open ? "true" : "false"); });
    if (open) { var c = $(".hr-contents__close", p); if (c) c.focus(); }
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-hr-contents-toggle]");
    if (t) { e.preventDefault(); var p = panel(); setContents(p && p.hidden); return; }
    var a = e.target.closest && e.target.closest("#hr-contents a");
    if (a) setContents(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { var p = panel(); if (p && !p.hidden) { setContents(false); var b = $(".hr-bar__contents"); if (b) b.focus(); } }
  });

  /* ---- progress bar ---- */
  var ticking = false;
  function progress() {
    ticking = false;
    var bar = $(".hr-progress span"); if (!bar) return;
    var body = $(".hr-body");
    if (!body || !$(".hr-page--story")) { bar.style.setProperty("--p", 0); return; }
    var r = body.getBoundingClientRect(), h = r.height - window.innerHeight * 0.6;
    var p = h > 0 ? Math.min(1, Math.max(0, (-r.top + window.innerHeight * 0.3) / h)) : 0;
    bar.style.setProperty("--p", p.toFixed(4));
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(progress); } }, { passive: true });

  /* ---- scroll-spy ---- */
  var spy;
  function initSpy() {
    if (spy) { spy.disconnect(); spy = null; }
    var links = $$(".hr-rail__list a"); if (!links.length || !("IntersectionObserver" in window)) return;
    var map = {};
    links.forEach(function (a) { var id = decodeURIComponent((a.getAttribute("href") || "").replace(/^#/, "")); var el = id && document.getElementById(id); if (el) map[id] = { a: a, el: el }; });
    var ids = Object.keys(map); if (!ids.length) return;
    var current = null;
    function set(id) { if (id === current) return; current = id; links.forEach(function (a) { a.classList.remove("is-active"); a.removeAttribute("aria-current"); }); if (id && map[id]) { map[id].a.classList.add("is-active"); map[id].a.setAttribute("aria-current", "location"); } }
    spy = new IntersectionObserver(function () {
      var best = null, top = Infinity;
      ids.forEach(function (id) { var r = map[id].el.getBoundingClientRect(); if (r.top < window.innerHeight * 0.35 && (window.innerHeight * 0.35 - r.top) < top) { top = window.innerHeight * 0.35 - r.top; best = id; } });
      set(best);
    }, { rootMargin: "0px 0px -60% 0px", threshold: [0, 1] });
    ids.forEach(function (id) { spy.observe(map[id].el); });
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; spy && spy.takeRecords(); progress(); }); } }, { passive: true });
  }

  /* ---- header current state ---- */
  function markNav() {
    var path = location.pathname.replace(/index\.html$/, "");
    $$(".hr-bar__links a").forEach(function (a) {
      var u = new URL(a.getAttribute("href"), location.href).pathname.replace(/index\.html$/, "");
      var on = u.length > 1 && path.indexOf(u) === 0;
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
  }

  /* ---- table filter ---- */
  function tableFilters() {
    $$(".hr-body table").forEach(function (t) {
      var rows = $$("tbody tr", t).filter(function (r) { return !r.classList.contains("hr-letter"); });
      if (rows.length < 14 || t.dataset.hrf) return; t.dataset.hrf = 1;
      var wrap = t.closest(".md-typeset__scrollwrap") || t;
      var box = document.createElement("div"); box.className = "hr-tablefilter";
      box.innerHTML = '<label for="hrf-' + rows.length + '">Filter</label><input id="hrf-' + rows.length + '" type="search" placeholder="Type a name, year or place" autocomplete="off"><output aria-live="polite"></output>';
      wrap.parentNode.insertBefore(box, wrap);
      var input = $("input", box), out = $("output", box);
      input.addEventListener("input", function () {
        var q = input.value.trim().toLowerCase(), n = 0;
        rows.forEach(function (r) { var show = !q || r.textContent.toLowerCase().indexOf(q) > -1; r.hidden = !show; if (show) n++; });
        $$("tr.hr-letter", t).forEach(function (l) { var nx = l.nextElementSibling, any = false; while (nx && !nx.classList.contains("hr-letter")) { if (!nx.hidden) { any = true; break; } nx = nx.nextElementSibling; } l.hidden = !any; });
        out.textContent = q ? n + " of " + rows.length + " rows" : "";
      });
    });
  }

  /* ---- legacy record box fallback ---- */
  function chips() {
    $$(".admonition.abstract p, .admonition.abstract li").forEach(function (p) {
      if (p.dataset.hr) return; p.dataset.hr = 1;
      $$("strong", p).forEach(function (s) {
        if (!/^Confidence:?$/.test(s.textContent.trim())) return;
        var n = s.nextSibling; if (!n || n.nodeType !== 3) return;
        var m = n.textContent.match(/^\s*([^·]+?)\s*(·|$)/); if (!m) return;
        var v = m[1], c = document.createElement("span");
        c.className = "hr-chip " + (/^high/i.test(v) ? "hr-chip--high" : /^low/i.test(v) ? "hr-chip--low" : "hr-chip--mid");
        c.textContent = v; n.textContent = n.textContent.slice(m[0].length - (m[2] ? m[2].length : 0));
        s.after(" ", c, " ");
      });
    });
  }

  function boot() { setContents(false); markNav(); initSpy(); tableFilters(); chips(); progress(); }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
