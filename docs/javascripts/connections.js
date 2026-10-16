/* Web of influence: highlight a name's connections and filter by relationship type. Progressive enhancement:
   without JS the full diagram and the text table are still there. */
(function () {
  function init(root) {
    var svg = root.querySelector(".hr-web__svg");
    if (!svg || root.dataset.ready) return;
    root.dataset.ready = "1";
    var edges = [].slice.call(svg.querySelectorAll(".hr-web__edge"));
    var nodes = [].slice.call(svg.querySelectorAll(".hr-web__node"));
    var panel = root.querySelector("#hr-web-panel");
    var hint = panel ? panel.textContent : "";
    var off = {};
    function paint(id) {
      var on = {};
      edges.forEach(function (e) {
        var hidden = off[e.dataset.type];
        e.classList.toggle("is-hidden", !!hidden);
        var hit = id && !hidden && (e.dataset.a === id || e.dataset.b === id);
        e.classList.toggle("is-lit", !!hit);
        e.classList.toggle("is-dim", !!id && !hit);
        if (hit) { on[e.dataset.a] = 1; on[e.dataset.b] = 1; }
      });
      nodes.forEach(function (n) {
        n.classList.toggle("is-dim", !!id && !on[n.dataset.node]);
        n.classList.toggle("is-lit", !!id && !!on[n.dataset.node]);
      });
      if (panel) {
        if (!id) { panel.textContent = hint; return; }
        var items = edges.filter(function (e) { return !off[e.dataset.type] && (e.dataset.a === id || e.dataset.b === id); })
          .map(function (e) { return e.querySelector("title").textContent; });
        panel.textContent = items.length ? items.join("  •  ") : "No connections under the current filter.";
      }
    }
    var current = null;
    nodes.forEach(function (n) {
      n.addEventListener("mouseenter", function () { paint(n.dataset.node); });
      n.addEventListener("focus", function () { paint(n.dataset.node); });
      n.addEventListener("mouseleave", function () { paint(current); });
      n.addEventListener("blur", function () { paint(current); });
    });
    svg.addEventListener("click", function (ev) {
      if (!ev.target.closest(".hr-web__node")) { current = null; paint(null); }
    });
    [].slice.call(root.querySelectorAll("[data-filter]")).forEach(function (cb) {
      cb.addEventListener("change", function () { off[cb.dataset.filter] = !cb.checked; paint(current); });
    });
    paint(null);
  }
  function boot() { [].slice.call(document.querySelectorAll("[data-hr-web]")).forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(boot);
})();
