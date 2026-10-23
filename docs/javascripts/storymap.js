/* Story map (reference/story-map/): era and region chips, state shading, grouped pins, the pin sheet, pinch and
   button zoom. The page works without this file (the pins and the by-state list are in the HTML); this adds the
   filtering and the sheet. Data: assets/hr-map.json, written by hooks/map_hook.py. No third-party code. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg", W = 975, H = 610;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var data = null, loading = null;

  function base() { try { return new URL(JSON.parse($("#__config").textContent).base, location.href); } catch (e) { return new URL(document.baseURI); } }
  function siteUrl(u) { return new URL(u, base().href.replace(/\/?$/, "/")).href; }
  function esc(t) { var d = document.createElement("div"); d.textContent = t == null ? "" : t; return d.innerHTML; }
  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) loading = fetch(siteUrl("assets/hr-map.json")).then(function (r) { return r.json(); }).then(function (j) { data = j; return j; });
    return loading;
  }
  var ERA_TXT = { "": "all eras", "1930s": "the 1930s and earlier", "1980s": "the 1980s and later" };
  var ERA_BADGE = { e30: "1930s–40s", e50: "1950s", e60: "1960s", e70: "1970s", e80: "1980s+" };
  function eraText(e) { return ERA_TXT[e] || ("the " + e); }
  function plural(n, a, b) { return n + " " + (n === 1 ? a : (b || a + "s")); }
  function q(n) { return n <= 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 6 ? 3 : n <= 11 ? 4 : 5; }

  function init(root) {
    if (!root || root.dataset.ready) return;
    root.dataset.ready = "1";
    var svg = $("svg", root), pinsG = $(".hr-map__pins", svg), sheet = $(".hr-map__sheet", root);
    var countEl = $(".hr-map__count", root), stage = $(".hr-map__stage", root);
    var st = { era: "", region: "", vb: { x: 0, y: 0, w: W, h: H }, open: null };
    var params = new URLSearchParams(location.search);
    if (params.get("region")) { var rg = $(".hr-map__regions", root); if (rg) rg.hidden = false; var rb0 = $(".hr-map__regbtn", root); if (rb0) rb0.setAttribute("aria-expanded", "true"); }
    if (params.get("era")) st.era = params.get("era");
    if (params.get("region")) st.region = params.get("region");
    root.classList.add("hr-map--js");

    function match(s) {
      return (!st.era || s.b.indexOf(st.era) > -1) && (!st.region || s.r === st.region);
    }
    function unit() { var w = svg.getBoundingClientRect().width || W; return Math.max(st.vb.w / w, st.vb.h / (svg.getBoundingClientRect().height || H)); }
    function setVB() {
      var v = st.vb;
      svg.setAttribute("viewBox", v.x.toFixed(2) + " " + v.y.toFixed(2) + " " + v.w.toFixed(2) + " " + v.h.toFixed(2));
      var zoomed = v.w < W - 0.5;
      root.classList.toggle("hr-map--zoomed", zoomed);
      svg.style.touchAction = zoomed ? "none" : "pan-y";
    }
    function clampVB() {
      var v = st.vb;
      v.w = Math.max(W / 10, Math.min(W, v.w)); v.h = v.w * H / W;
      v.x = Math.max(0, Math.min(W - v.w, v.x)); v.y = Math.max(0, Math.min(H - v.h, v.y));
    }
    function zoomAt(cx, cy, f) {
      var v = st.vb, nw = Math.max(W / 10, Math.min(W, v.w / f)), k = nw / v.w;
      v.x = cx - (cx - v.x) * k; v.y = cy - (cy - v.y) * k; v.w = nw; v.h = nw * H / W;
      clampVB(); setVB(); schedule();
    }
    function toSvg(clientX, clientY) {
      var r = svg.getBoundingClientRect(), u = unit();
      // preserveAspectRatio meet: centre the frame inside the element box
      var ox = (r.width - st.vb.w / u) / 2, oy = (r.height - st.vb.h / u) / 2;
      return { x: st.vb.x + (clientX - r.left - ox) * u, y: st.vb.y + (clientY - r.top - oy) * u };
    }

    /* ---- render ---- */
    var clusters = [], raf = 0;
    function schedule() { if (!raf) raf = requestAnimationFrame(function () { raf = 0; render(); }); }
    function render() {
      if (!data) return;
      var ok = data.stories.map(match), u = unit();
      // state shading
      var counts = {};
      data.stories.forEach(function (s, i) { if (ok[i]) (s.sts || []).forEach(function (a) { counts[a] = (counts[a] || 0) + 1; }); });
      $$(".hr-map__st", svg).forEach(function (p) {
        var n = counts[p.dataset.st] || 0;
        p.setAttribute("class", "hr-map__st q" + q(n));
        var t = p.querySelector("title"); if (t) t.textContent = (data.states[p.dataset.st] || p.dataset.st) + ": " + plural(n, "story", "stories");
      });
      // pins grouped by screen distance
      var vis = [];
      data.pins.forEach(function (p, i) {
        var xs = p.x.filter(function (k) { return ok[k]; });
        if (xs.length) vis.push({ i: i, p: p, xs: xs });
      });
      vis.sort(function (a, b) { return b.xs.length - a.xs.length || a.i - b.i; });
      var R = 22 * u; clusters = [];
      vis.forEach(function (v) {
        for (var c = 0; c < clusters.length; c++) {
          var cl = clusters[c], dx = cl.x - v.p.x0, dy = cl.y - v.p.y0;
          if (dx * dx + dy * dy < R * R) { cl.members.push(v); return; }
        }
        clusters.push({ x: v.p.x0, y: v.p.y0, members: [v] });
      });
      while (pinsG.firstChild) pinsG.removeChild(pinsG.firstChild);
      clusters.forEach(function (cl, ci) {
        var ids = {}, n = 0;
        cl.members.forEach(function (m) { m.xs.forEach(function (k) { if (!ids[k]) { ids[k] = 1; n++; } }); });
        cl.n = n;
        var towns = cl.members.length, r = Math.min(16, 6.5 + 2.2 * Math.sqrt(n));
        var g = document.createElementNS(NS, "g");
        g.setAttribute("class", "hr-pin" + (towns > 1 ? " hr-pin--group" : "") + (st.open && st.open.ci === ci ? " is-open" : ""));
        g.setAttribute("transform", "translate(" + cl.x + " " + cl.y + ") scale(" + u.toFixed(4) + ")");
        g.setAttribute("tabindex", "0"); g.setAttribute("role", "button");
        g.dataset.ci = ci;
        var label = towns > 1 ? cl.members[0].p.n + " and " + plural(towns - 1, "nearby town") : cl.members[0].p.n;
        g.setAttribute("aria-label", label + ": " + plural(n, "story", "stories"));
        var hit = document.createElementNS(NS, "circle"); hit.setAttribute("r", 22); hit.setAttribute("class", "hr-pin__hit"); g.appendChild(hit);
        if (towns > 1) { var ring = document.createElementNS(NS, "circle"); ring.setAttribute("r", r + 3.5); ring.setAttribute("class", "hr-pin__ring"); g.appendChild(ring); }
        var dot = document.createElementNS(NS, "circle"); dot.setAttribute("r", r); dot.setAttribute("class", "hr-pin__dot"); g.appendChild(dot);
        if (n > 1) { var t = document.createElementNS(NS, "text"); t.setAttribute("class", "hr-pin__n"); t.setAttribute("dy", "0.36em"); t.textContent = n; g.appendChild(t); }
        pinsG.appendChild(g);
      });
      // running count
      var total = ok.filter(Boolean).length, places = vis.length;
      countEl.innerHTML = "<b>" + total + "</b> " + (total === 1 ? "story" : "stories") + " in " + esc(eraText(st.era)) +
        (st.region ? ", <b>" + esc(st.region) + "</b>" : "") + " · <b>" + places + "</b> " + (places === 1 ? "place" : "places");
      root.dataset.era = st.era ? ({ "1930s": "e30", "1940s": "e30", "1950s": "e50", "1960s": "e60", "1970s": "e70", "1980s": "e80" })[st.era] : "";
      if (!st.era) root.removeAttribute("data-era");
      $$("[data-era-chip]", root).forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.eraChip === st.era ? "true" : "false"); });
      $$("[data-region-chip]", root).forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.regionChip === st.region ? "true" : "false"); });
      var more = $(".hr-map__regbtn", root); if (more) more.textContent = st.region ? "Region: " + st.region : "Region";
      if (st.open && st.open.kind === "state") fillState(st.open.st);
      else if (!st.open && wide()) showDefault(counts, total);
    }
    function wide() { return window.matchMedia && matchMedia("(min-width: 62em)").matches; }
    function showDefault(counts, total) {
      var rows = Object.keys(counts).filter(function (a) { return counts[a] > 0; }).sort(function (a, b) { return counts[b] - counts[a] || (data.states[a] < data.states[b] ? -1 : 1); });
      var html = '<p class="hr-map__where">Tap a pin for that town\'s stories, or a state for every story that touches it. The states with the most stories for this filter:</p>';
      html += rows.length ? '<ol class="hr-map__rank">' + rows.slice(0, 12).map(function (a) {
        return '<li><button type="button" data-state="' + a + '"><span>' + esc(data.states[a] || a) + '</span><b>' + counts[a] + "</b></button></li>";
      }).join("") + "</ol>" : '<p class="hr-map__where">No stories match this filter yet.</p>';
      if (rows.length > 12) html += '<p class="hr-map__where">…and ' + plural(rows.length - 12, "more state") + ".</p>";
      $(".hr-map__kicker", sheet).textContent = plural(total, "story", "stories") + " · " + eraText(st.era) + (st.region ? " · " + st.region : "");
      $(".hr-map__h", sheet).textContent = "Where the stories are";
      $(".hr-map__body", sheet).innerHTML = html;
      sheet.hidden = false; root.classList.add("hr-map--default"); root.classList.remove("hr-map--sheet");
    }

    /* ---- sheet ---- */
    function storyLi(k) {
      var s = data.stories[k];
      return '<li><a href="' + esc(siteUrl(s.u)) + '"><span class="hr-map__badge"' + (s.k ? ' data-era="' + s.k + '"' : "") + ">" + esc(ERA_BADGE[s.k] || s.e || "") + "</span>" +
        "<strong>" + esc(s.t) + "</strong><span class=\"hr-map__sum\">" + esc(s.s) + '</span><em class="hr-map__go">Read the full story &rarr;</em></a></li>';
    }
    function sortEra(xs) {
      if (!st.era) return xs;
      var hit = function (k) { var e = data.stories[k].e || ""; return e === st.era || (st.era === "1930s" && e < "1940s") || (st.era === "1980s" && e >= "1980s") ? 0 : 1; };
      return xs.slice().sort(function (a, b) { return hit(a) - hit(b); });
    }
    function prec(p) { return p.pr === "site" ? "pinned at the site" : p.pr === "county" ? "pinned at the county centre" : "pinned at the town centre"; }
    function openSheet(html, kicker, title) {
      $(".hr-map__kicker", sheet).textContent = kicker;
      $(".hr-map__h", sheet).textContent = title;
      $(".hr-map__body", sheet).innerHTML = html;
      $(".hr-map__body", sheet).scrollTop = 0;
      sheet.hidden = false; root.classList.add("hr-map--sheet"); root.classList.remove("hr-map--default");
      var x = $(".hr-map__close", sheet); if (x) x.focus({ preventScroll: true });
    }
    function closeSheet() {
      if (sheet.hidden || !st.open) return;
      if (!wide()) sheet.hidden = true;
      root.classList.remove("hr-map--sheet");
      var was = st.open; st.open = null; schedule(); setUrl();
      if (was && was.el && document.contains(was.el)) was.el.focus({ preventScroll: true });
    }
    function townBlock(m, many) {
      var p = m.p, other = p.x.filter(function (k) { return m.xs.indexOf(k) < 0; });
      var h = many ? '<h3 class="hr-map__town">' + esc(p.n) + "</h3>" : "";
      h += '<p class="hr-map__where">' + esc(prec(p)) + (p.strips && p.strips.length ? " · strips: " + esc(p.strips.join(", ")) : "") + "</p>";
      h += '<ul class="hr-map__stories">' + sortEra(m.xs).map(storyLi).join("") + "</ul>";
      if (other.length) h += '<details class="hr-map__other"><summary>' + plural(other.length, "more story", "more stories") + " here from other eras or regions</summary><ul class=\"hr-map__stories\">" + other.map(storyLi).join("") + "</ul></details>";
      return h;
    }
    function openCluster(ci, el) {
      var cl = clusters[ci]; if (!cl) return;
      st.open = { kind: "pin", ci: ci, id: cl.members[0].p.id, el: el };
      var many = cl.members.length > 1;
      var html = many ? '<p class="hr-map__zoomrow"><button type="button" class="hr-linkbtn" data-zoom-to="' + ci + '">Zoom in to separate these ' + cl.members.length + " towns</button></p>" : "";
      html += cl.members.map(function (m) { return townBlock(m, many); }).join("");
      var p0 = cl.members[0].p;
      openSheet(html, plural(cl.n, "story", "stories") + " · " + eraText(st.era), many ? p0.n + " and " + plural(cl.members.length - 1, "nearby town") : p0.n);
      schedule(); setUrl();
    }
    function fillState(ab) {
      var ok = data.stories.map(match), list = [];
      data.stories.forEach(function (s, i) { if (ok[i] && (s.sts || []).indexOf(ab) > -1) list.push(i); });
      var html = list.length ? '<ul class="hr-map__stories">' + sortEra(list).map(storyLi).join("") + "</ul>" : '<p class="hr-map__where">No stories here for this filter yet. Know one? <a href="https://github.com/obnovas/hotrod-wiki/issues/new?template=suggestion-feedback.yml">Tell us</a>.</p>';
      $(".hr-map__kicker", sheet).textContent = plural(list.length, "story", "stories") + " · " + eraText(st.era);
      $(".hr-map__body", sheet).innerHTML = html;
    }
    function openState(ab, el) {
      st.open = { kind: "state", st: ab, el: el };
      openSheet("", "", data.states[ab] || ab); fillState(ab); setUrl();
    }
    function setUrl() {
      try {
        var p = new URLSearchParams();
        if (st.era) p.set("era", st.era);
        if (st.region) p.set("region", st.region);
        if (st.open && st.open.kind === "pin") p.set("place", st.open.id);
        if (st.open && st.open.kind === "state") p.set("state", st.open.st);
        var s = p.toString();
        history.replaceState(history.state, "", location.pathname + (s ? "?" + s : "") + location.hash);
      } catch (e) {}
    }

    /* ---- input ---- */
    root.addEventListener("click", function (e) {
      var t = e.target;
      var ec = t.closest("[data-era-chip]");
      if (ec) { st.era = ec.dataset.eraChip; if (st.open && st.open.kind === "pin") closeSheet(); render(); setUrl(); return; }
      var rc = t.closest("[data-region-chip]");
      if (rc) { st.region = st.region === rc.dataset.regionChip ? "" : rc.dataset.regionChip; if (st.open && st.open.kind === "pin") closeSheet(); render(); setUrl(); return; }
      var z = t.closest("[data-zoom]");
      if (z) {
        var v = st.vb, cx = v.x + v.w / 2, cy = v.y + v.h / 2;
        if (z.dataset.zoom === "in") zoomAt(cx, cy, 1.8); else if (z.dataset.zoom === "out") zoomAt(cx, cy, 1 / 1.8);
        else { st.vb = { x: 0, y: 0, w: W, h: H }; setVB(); schedule(); }
        return;
      }
      var zt = t.closest("[data-zoom-to]");
      if (zt) {
        var cl = clusters[+zt.dataset.zoomTo];
        if (cl) {
          var xs = cl.members.map(function (m) { return m.p.x0; }), ys = cl.members.map(function (m) { return m.p.y0; });
          var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
          var w = Math.max((x1 - x0) * 3.2, (y1 - y0) * 3.2 * W / H, W / 10);
          st.vb = { x: (x0 + x1) / 2 - w / 2, y: (y0 + y1) / 2 - w * H / W / 2, w: w, h: w * H / W };
          clampVB(); closeSheet(); setVB(); schedule();
          stage.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
        }
        return;
      }
      if (t.closest(".hr-map__close")) { closeSheet(); return; }
      var sb = t.closest("[data-state]");
      if (sb) { openState(sb.dataset.state, sb); return; }
      var rb = t.closest(".hr-map__regbtn");
      if (rb) { var open = rb.getAttribute("aria-expanded") !== "true"; rb.setAttribute("aria-expanded", open ? "true" : "false"); $(".hr-map__regions", root).hidden = !open; return; }
    });
    sheet.addEventListener("click", function (e) { if (e.target === sheet) closeSheet(); });
    document.addEventListener("keydown", function (e) {
      if (!document.contains(root)) return;
      if (e.key === "Escape") { closeSheet(); return; }
      var g = e.target.closest && e.target.closest(".hr-pin");
      if (g && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openCluster(+g.dataset.ci, g); }
    });

    // pointer: tap a pin or a state; drag to pan when zoomed; two fingers to pinch
    var pts = {}, start = null, moved = false, pinch = null;
    svg.addEventListener("pointerdown", function (e) {
      if (e.isPrimary) { pts = {}; pinch = null; } // a new first finger: drop any touch whose "up" never arrived
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      var ids = Object.keys(pts);
      if (ids.length === 1) { start = { x: e.clientX, y: e.clientY, vb: { x: st.vb.x, y: st.vb.y, w: st.vb.w, h: st.vb.h } }; moved = false; }
      if (ids.length === 2) {
        var a = pts[ids[0]], b = pts[ids[1]];
        pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), w: st.vb.w, c: toSvg((a.x + b.x) / 2, (a.y + b.y) / 2) };
        moved = true;
        try { svg.setPointerCapture(e.pointerId); } catch (x) {}
      }
    });
    svg.addEventListener("pointermove", function (e) {
      if (!pts[e.pointerId]) return;
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      var ids = Object.keys(pts);
      if (ids.length === 2 && pinch) {
        var a = pts[ids[0]], b = pts[ids[1]], d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d > 0 && pinch.d > 0) {
          var nw = Math.max(W / 10, Math.min(W, pinch.w * pinch.d / d)), c = pinch.c, mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
          var r = svg.getBoundingClientRect(), u = Math.max(nw / r.width, nw * H / W / r.height);
          var ox = (r.width - nw / u) / 2, oy = (r.height - nw * H / W / u) / 2;
          st.vb = { x: c.x - (mid.x - r.left - ox) * u, y: c.y - (mid.y - r.top - oy) * u, w: nw, h: nw * H / W };
          clampVB(); setVB(); schedule();
        }
        e.preventDefault(); return;
      }
      if (ids.length === 1 && start) {
        var dx = e.clientX - start.x, dy = e.clientY - start.y;
        if (Math.abs(dx) + Math.abs(dy) > 8) moved = true;
        if (moved && st.vb.w < W - 0.5) {
          var u2 = unit();
          st.vb.x = start.vb.x - dx * u2; st.vb.y = start.vb.y - dy * u2; clampVB(); setVB(); schedule();
          e.preventDefault();
        }
      }
    });
    function up(e) {
      var was = pts[e.pointerId]; delete pts[e.pointerId];
      if (Object.keys(pts).length < 2) pinch = null;
      if (!was || moved || Object.keys(pts).length) { if (!Object.keys(pts).length) start = null; return; }
      start = null;
      if (e.type === "pointercancel") return;
      var g = e.target.closest && e.target.closest(".hr-pin");
      if (g && g.dataset.ci != null) { openCluster(+g.dataset.ci, g); return; }
      var s = e.target.closest && e.target.closest(".hr-map__st");
      if (s && data) openState(s.dataset.st, null);
    }
    svg.addEventListener("pointerup", up);
    svg.addEventListener("pointercancel", up);
    svg.addEventListener("wheel", function (e) {
      if (!(e.ctrlKey || e.metaKey)) return; // trackpad pinch arrives as ctrl+wheel; plain wheel scrolls the page
      e.preventDefault();
      var c = toSvg(e.clientX, e.clientY); zoomAt(c.x, c.y, Math.exp(-e.deltaY * 0.01));
    }, { passive: false });
    svg.addEventListener("dblclick", function (e) { var c = toSvg(e.clientX, e.clientY); zoomAt(c.x, c.y, 2); });
    window.addEventListener("resize", function () { if (!wide() && !st.open) { sheet.hidden = true; root.classList.remove("hr-map--default"); } schedule(); });

    load().then(function () {
      render(); setVB();
      var place = params.get("place"), stt = params.get("state");
      if (place) {
        for (var i = 0; i < clusters.length; i++) {
          if (clusters[i].members.some(function (m) { return m.p.id === place; })) { openCluster(i, null); break; }
        }
      } else if (stt && data.states[stt]) openState(stt, null);
    }).catch(function () { root.classList.remove("hr-map--js"); });
  }

  function boot() { init(document.getElementById("hr-map")); }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
