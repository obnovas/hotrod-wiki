// Highlights carousel. Progressive enhancement: the server-rendered <ul> is a complete static list without JS.
(function () {
  "use strict";
  var INTERVAL_DEFAULT = 7000;

  function init(root) {
    if (!root || root.dataset.hrInit) return;
    root.dataset.hrInit = "1";
    root.classList.add("hr-hl--js");
    var viewport = root.querySelector(".hr-hl-viewport");
    var track = root.querySelector(".hr-hl-track");
    var slides = Array.prototype.slice.call(track.children);
    var n = slides.length;
    if (n < 2) return;
    var mql = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false, addEventListener: function () {} };
    var reduced = mql.matches;
    var interval = parseInt(root.dataset.autoplay, 10) || INTERVAL_DEFAULT;
    var i = 0, timer = null, userPaused = reduced, hoverPause = false, focusPause = false, offscreen = false;

    root.classList.toggle("hr-hl--reduced", reduced);
    track.id = track.id || "hr-hl-track";

    // controls
    var controls = document.createElement("div");
    controls.className = "hr-hl-controls";
    controls.innerHTML =
      '<button type="button" class="hr-hl-btn hr-hl-prev" aria-label="Previous highlight" aria-controls="' + track.id + '"><span aria-hidden="true">&#8249;</span></button>' +
      '<button type="button" class="hr-hl-btn hr-hl-toggle" aria-label="Pause automatic rotation"><span aria-hidden="true">&#10074;&#10074;</span></button>' +
      '<div class="hr-hl-dots" role="tablist" aria-label="Choose a highlight"></div>' +
      '<span class="hr-hl-count" aria-hidden="true"></span>' +
      '<button type="button" class="hr-hl-btn hr-hl-next" aria-label="Next highlight" aria-controls="' + track.id + '"><span aria-hidden="true">&#8250;</span></button>';
    var frame = document.createElement("div");
    frame.className = "hr-hl-frame";
    viewport.before(frame);
    frame.appendChild(viewport);
    frame.appendChild(controls);
    var legend = document.createElement("p");
    legend.className = "hr-hl-legend";
    legend.textContent = "Square dots mark local and grassroots highlights.";
    frame.after(legend);

    var prev = controls.querySelector(".hr-hl-prev");
    var next = controls.querySelector(".hr-hl-next");
    var toggle = controls.querySelector(".hr-hl-toggle");
    var dotsEl = controls.querySelector(".hr-hl-dots");
    var count = controls.querySelector(".hr-hl-count");
    var live = document.createElement("div");
    live.className = "hr-sr"; live.setAttribute("aria-live", "polite"); live.setAttribute("role", "status");
    root.appendChild(live);

    var dots = slides.map(function (s, k) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "hr-hl-dot"; b.setAttribute("role", "tab");
      b.setAttribute("aria-label", "Highlight " + (k + 1) + " of " + n);
      b.dataset.g = s.dataset.grassroots === "true" ? "true" : "false";
      b.addEventListener("click", function () { userPaused = true; syncToggle(); go(k, true); });
      dotsEl.appendChild(b);
      return b;
    });

    function show(k) {
      slides.forEach(function (s, j) {
        var on = j === k;
        s.setAttribute("aria-hidden", on ? "false" : "true");
        if ("inert" in s) s.inert = !on; else Array.prototype.forEach.call(s.querySelectorAll("a"), function (a) { a.tabIndex = on ? 0 : -1; });
        dots[j].setAttribute("aria-selected", on ? "true" : "false");
        dots[j].tabIndex = on ? 0 : -1;
      });
      track.style.transform = "translateX(" + (-100 * k) + "%)";
      count.textContent = (k + 1) + " / " + n;
    }
    function go(k, announce) {
      i = (k + n) % n;
      show(i);
      if (announce) live.textContent = "Highlight " + (i + 1) + " of " + n + ": " + (slides[i].querySelector("h3") || {}).textContent;
      restart();
    }
    function shouldPlay() { return !userPaused && !hoverPause && !focusPause && !offscreen && !document.hidden && !reduced; }
    function restart() {
      clearInterval(timer); timer = null;
      track.setAttribute("aria-live", "off");
      if (shouldPlay()) timer = setInterval(function () { go(i + 1, false); }, interval);
      else track.setAttribute("aria-live", "polite");
    }
    function syncToggle() {
      var paused = userPaused;
      toggle.setAttribute("aria-label", paused ? "Start automatic rotation" : "Pause automatic rotation");
      toggle.firstChild.innerHTML = paused ? "&#9654;" : "&#10074;&#10074;";
      toggle.setAttribute("aria-pressed", paused ? "true" : "false");
      restart();
    }

    prev.addEventListener("click", function () { userPaused = true; syncToggle(); go(i - 1, true); });
    next.addEventListener("click", function () { userPaused = true; syncToggle(); go(i + 1, true); });
    toggle.addEventListener("click", function () { userPaused = !userPaused; syncToggle(); });

    // pause on hover / focus
    root.addEventListener("mouseenter", function () { hoverPause = true; restart(); });
    root.addEventListener("mouseleave", function () { hoverPause = false; restart(); });
    root.addEventListener("focusin", function () { focusPause = true; restart(); });
    root.addEventListener("focusout", function (e) { if (!root.contains(e.relatedTarget)) { focusPause = false; restart(); } });

    // keyboard: arrows / Home / End anywhere inside the carousel
    root.addEventListener("keydown", function (e) {
      var k = e.key;
      if (k === "ArrowRight" || k === "ArrowLeft" || k === "Home" || k === "End") {
        if (e.target.closest && e.target.closest("input,textarea,select")) return;
        e.preventDefault(); userPaused = true; syncToggle();
        go(k === "ArrowRight" ? i + 1 : k === "ArrowLeft" ? i - 1 : k === "Home" ? 0 : n - 1, true);
        var d = dots[i]; if (d && e.target.classList && e.target.classList.contains("hr-hl-dot")) d.focus();
      }
    });

    // swipe (pointer events; vertical scrolling stays native thanks to touch-action: pan-y)
    var sx = null, sy = null, moved = false;
    viewport.addEventListener("pointerdown", function (e) { if (e.pointerType === "mouse" && e.button !== 0) return; sx = e.clientX; sy = e.clientY; moved = false; });
    viewport.addEventListener("pointerup", function (e) {
      if (sx === null) return;
      var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) { moved = true; userPaused = true; syncToggle(); go(i + (dx < 0 ? 1 : -1), true); }
    });
    viewport.addEventListener("pointercancel", function () { sx = null; });
    viewport.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);

    // visibility: don't rotate off-screen or in a background tab
    document.addEventListener("visibilitychange", restart);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { offscreen = !en[0].isIntersecting; restart(); }, { threshold: 0.2 }).observe(root);
    }
    var onMotion = function (e) { reduced = e.matches; root.classList.toggle("hr-hl--reduced", reduced); if (reduced) userPaused = true; syncToggle(); };
    if (mql.addEventListener) mql.addEventListener("change", onMotion);

    show(0); syncToggle();
  }

  function boot() { init(document.getElementById("hr-highlights")); }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
