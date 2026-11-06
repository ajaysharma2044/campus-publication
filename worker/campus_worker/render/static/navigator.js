/* Progressive enhancement for the process navigator (continuous-local-run R47). The server renders a complete
   answer for the selected path; this script re-resolves the path in place from the embedded graph when the
   selects change. Mirrors tools/navigator.py: L1 transition + every L2/L3 node whose situation is selected,
   child rules override parent rules. Keyboard-usable: plain selects, checkboxes and a submit button. */
(function () {
  "use strict";
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function list(title, items, tag) {
    if (!items || !items.length) return "";
    return "<h3>" + esc(title) + "</h3><" + tag + ">" + items.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</" + tag + ">";
  }
  function resolve(graph, from, to, situations) {
    var l1 = graph.nodes.filter(function (n) { return n.layer === 1 && n.from_state === from && n.to_state === to; })[0];
    if (!l1) return { found: false, message: "No documented path from " + from + " to " + to + " on the official pages we hold. Ask the receiving college's advising office." };
    var byId = {}; graph.nodes.forEach(function (n) { byId[n.id] = n; });
    var applicable = [l1];
    graph.nodes.filter(function (n) { return n.layer > 1; }).forEach(function (n) {
      var p = n, under = false;
      while (p && p.parent_id) { p = byId[p.parent_id]; if (p && p.id === l1.id) { under = true; break; } }
      if (under && n.situation && situations.indexOf(n.situation) >= 0) applicable.push(n);
    });
    applicable.sort(function (a, b) { return a.layer - b.layer; });
    var rules = {};
    applicable.forEach(function (n) { var chain = []; var p = n; while (p) { chain.unshift(p); p = p.parent_id ? byId[p.parent_id] : null; }
      chain.forEach(function (c) { if (!c.inherits_parent) Object.keys(c.rules || {}).forEach(function (k) { rules[k] = c.rules[k]; }); }); });
    return { found: true, nodes: applicable, rules: rules };
  }
  function render(result, out) {
    if (!result.found) { out.innerHTML = '<h2>No documented path</h2><p class="value-unknown">' + esc(result.message) + "</p>"; return; }
    var r = result.rules, h = "<h2>" + esc(result.nodes.map(function (n) { return n.label; }).join(" · ")) + "</h2>";
    h += list("Steps", r.steps, "ol");
    var req = []; if (r.gpa_min) req.push("Minimum GPA: " + r.gpa_min); (r.prerequisites || []).forEach(function (p) { req.push("Prerequisite: " + p); }); (r.course_requirements || []).forEach(function (c) { req.push(c); });
    h += list("Requirements", req, "ul") + list("Deadlines", r.deadlines, "ul") + list("Forms", r.forms, "ul") + list("Office that owns this", r.offices, "ul") + list("Exceptions", r.exceptions, "ul");
    out.innerHTML = h;
  }
  function enhance(form) {
    var el = form.querySelector("[data-graph]"); if (!el) return;
    var graph; try { graph = JSON.parse(el.textContent); } catch (e) { return; }
    var out = form.querySelector("[data-result]");
    function update() {
      var from = form.querySelector("[data-from]").value, to = form.querySelector("[data-to]").value;
      var sits = Array.prototype.map.call(form.querySelectorAll("[data-situation]:checked"), function (c) { return c.value; });
      render(resolve(graph, from, to, sits), out);
    }
    form.addEventListener("change", update);
    form.addEventListener("submit", function (e) { e.preventDefault(); update(); });
  }
  document.querySelectorAll("form[data-navigator]").forEach(enhance);
})();
