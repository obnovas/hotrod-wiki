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


  /* ==================== round 5: reading flow & wayfinding ==================== */
  var mq = function (q) { return window.matchMedia && matchMedia(q).matches; };
  var narrow = function () { return mq("(max-width: 62em)"); };

  /* folds: open on desktop (and without JS), folded on phones */
  function folds() {
    var phone = mq("(max-width: 52em)"), tablet = narrow();
    $$("[data-hr-rec]").forEach(function (d) { d.open = !phone; });
    $$("[data-hr-jump]").forEach(function (d) { d.open = !tablet; });
    $$("[data-hr-src]").forEach(function (d) { d.open = !tablet; });
    var here = location.pathname;
    $$(".hr-dept-block").forEach(function (li) {
      var hub = new URL(li.getAttribute("data-hr-hub") || "", document.baseURI).pathname;
      var d = $(".hr-dept-block__d", li), on = hub.length > 1 && here.indexOf(hub) === 0;
      li.classList.toggle("is-here", on);
      if (d) d.open = !tablet || on;
    });
  }

  /* any link or hash that lands inside a folded section unfolds it first */
  function reveal(id) {
    if (!id) return null;
    var el = document.getElementById(id); if (!el) return null;
    var p = el.parentElement;
    while (p) { if (p.tagName === "DETAILS" && !p.open) p.open = true; p = p.parentElement; }
    return el;
  }
  function onHash() { var id = decodeURIComponent(location.hash.replace(/^#/, "")); var el = reveal(id); if (el) setTimeout(function () { el.scrollIntoView({ block: "start" }); }, 0); }
  window.addEventListener("hashchange", onHash);

  /* footnote sheet on phones and tablets */
  var lastRef = null;
  function sheet() { return $("#hr-sheet"); }
  function closeSheet() { var s = sheet(); if (!s || s.hidden) return; s.hidden = true; document.documentElement.classList.remove("hr-sheet-open"); if (lastRef) lastRef.focus(); }
  function openSheet(a) {
    var s = sheet(); if (!s) return false;
    var id = decodeURIComponent((a.hash || "").replace(/^#/, "")), li = document.getElementById(id);
    if (!li) return false;
    var body = $(".hr-sheet__body", s), c = li.cloneNode(true);
    $$(".footnote-backref", c).forEach(function (b) { b.remove(); });
    body.innerHTML = c.innerHTML;
    $(".hr-sheet__h", s).textContent = "Note " + (a.textContent || "").trim();
    lastRef = a; s.hidden = false;
    var x = $(".hr-sheet__close", s); if (x) x.focus();
    return true;
  }

  /* back to top */
  function topBtn() {
    var b = $(".hr-totop"); if (!b) return;
    var show = window.scrollY > window.innerHeight * 1.3 && !!$(".hr-story");
    if (b.hidden === show) b.hidden = !show;
  }
  window.addEventListener("scroll", function () { requestAnimationFrame(topBtn); }, { passive: true });

  document.addEventListener("click", function (e) {
    var t = e.target;
    var fr = t.closest && t.closest(".hr-body a.footnote-ref");
    if (fr && narrow()) { if (openSheet(fr)) { e.preventDefault(); e.stopPropagation(); } return; }
    if (t.closest && t.closest(".hr-sheet__close")) { closeSheet(); return; }
    if (t.classList && t.classList.contains("hr-sheet")) { closeSheet(); return; }
    var all = t.closest && t.closest(".hr-sheet__all");
    if (all) { e.preventDefault(); closeSheet(); var el = reveal("hr-sources"); if (el) el.scrollIntoView({ block: "start" }); return; }
    var up = t.closest && t.closest("[data-hr-top]");
    if (up) { e.preventDefault(); window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); var h = $(".hr-headline") || $("h1"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); } return; }
    var a = t.closest && t.closest("a[href]");
    if (a && a.hash && a.pathname === location.pathname) { var id = decodeURIComponent(a.hash.slice(1)); if (id) reveal(id); }
  }, true);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSheet(); });

  /* hub filters: era / region / topic over the metadata cards */
  function hubFilters() {
    $$("[data-hr-filter]").forEach(function (f) {
      if (f.dataset.ready) return; f.dataset.ready = 1; f.hidden = false;
      var hub = f.closest("[data-hr-hub]"), cards = $$(".hr-sc", hub), out = $(".hr-filter__out", f), none = $(".hr-filter__none", hub), reset = $(".hr-filter__reset", f);
      function val(n) { var el = f.querySelector('[name="' + n + '"]:checked') || f.querySelector('select[name="' + n + '"]'); return el ? el.value : ""; }
      function apply() {
        var era = val("era"), reg = val("region"), tag = val("tag"), n = 0;
        cards.forEach(function (c) {
          var ok = (!era || (" " + c.dataset.eras + " ").indexOf(" " + era + " ") > -1) && (!reg || c.dataset.region === reg) && (!tag || (" " + c.dataset.tags + " ").indexOf(" " + tag + " ") > -1);
          c.hidden = !ok; if (ok) n++;
        });
        $$(".hr-stories__grp", hub).forEach(function (g) { g.hidden = !$$(".hr-sc", g).some(function (c) { return !c.hidden; }); });
        var any = era || reg || tag;
        out.textContent = any ? "Showing " + n + " of " + cards.length + " stories" : "";
        if (reset) reset.hidden = !any;
        if (none) none.hidden = n > 0;
      }
      function clear() { $$('input[value=""]', f).forEach(function (i) { i.checked = true; }); $$("select", f).forEach(function (s) { s.value = ""; }); apply(); }
      f.addEventListener("change", apply);
      if (reset) reset.addEventListener("click", clear);
      $$("[data-hr-filter-reset]", hub).forEach(function (b) { b.addEventListener("click", clear); });
    });
  }

  /* search results: summary + department/era/place chips + "Read the full story" */
  var cards = null, loading = null;
  function base() { try { return new URL(JSON.parse($("#__config").textContent).base, location.href); } catch (e) { return new URL(document.baseURI); } }
  function loadCards() {
    if (cards || loading) return loading;
    loading = fetch(new URL("assets/hr-cards.json", base().href.replace(/\/?$/, "/"))).then(function (r) { return r.json(); }).then(function (j) { cards = j; decorate(); }).catch(function () {});
    return loading;
  }
  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
  function decorate() {
    if (!cards) { loadCards(); return; }
    var b = base().pathname.replace(/\/?$/, "/");
    $$(".md-search-result__item").forEach(function (li) {
      if (li.dataset.hr) return;
      var a = $("a.md-search-result__link", li); if (!a) return;
      var u = new URL(a.getAttribute("href"), location.href), path = u.pathname;
      var key = path.indexOf(b) === 0 ? path.slice(b.length) : path.replace(/^\//, "");
      var c = cards[key]; li.dataset.hr = 1; if (!c) return;
      var h = $("article h1", a) || $("article h2", a); if (!h) return;
      var chips = [];
      if (c.d) chips.push('<span class="hr-sr-card__dept">' + esc(c.d) + "</span>");
      (c.e || []).slice(0, 3).forEach(function (e) { chips.push("<span>" + esc(e) + "</span>"); });
      if (c.p) chips.push("<span>" + esc(c.p) + "</span>");
      var box = document.createElement("div"); box.className = "hr-sr-card";
      box.innerHTML = (chips.length ? '<p class="hr-sr-card__chips">' + chips.join("") + "</p>" : "") + (c.s ? '<p class="hr-sr-card__sum">' + esc(c.s) + "</p>" : "") + (c.k === "story" ? '<span class="hr-sr-card__go">Read the full story →</span>' : "");
      h.after(box);
      var nx = box.nextElementSibling;
      if (nx && nx.tagName === "P" && c.s && nx.textContent.trim().slice(0, 40) === c.s.slice(0, 40)) nx.remove();
    });
  }
  function watchSearch() {
    var list = $(".md-search-result__list"); if (!list || list.dataset.hrw) return; list.dataset.hrw = 1;
    new MutationObserver(function () { decorate(); }).observe(list, { childList: true });
    var inp = $(".md-search__input"); if (inp) inp.addEventListener("focus", loadCards, { once: true });
  }

  function boot() { setContents(false); markNav(); initSpy(); tableFilters(); chips(); progress(); folds(); hubFilters(); watchSearch(); closeSheet(); topBtn(); if (location.hash) onHash(); }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
