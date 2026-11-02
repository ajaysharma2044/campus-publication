/* Progressive enhancement for the total-cost calculator. The server renders a complete, usable
   form and explanation; this script only recalculates in place. Mirrors tools/calculator.py.
   No analytics or ad calls here. */
(function () {
  "use strict";
  var DEFAULTS = { months_in_academic_year: 9, semesters_in_academic_year: 2, terms_in_academic_year: 2, weeks_in_academic_year: 36, days_in_academic_year: 270 };

  function toAY(amount, period, a) {
    switch (period) {
      case "per_academic_year": case "per_year": case "one_time": return amount;
      case "per_semester": return amount * a.semesters_in_academic_year;
      case "per_term": return amount * a.terms_in_academic_year;
      case "per_month": return amount * a.months_in_academic_year;
      case "per_week": return amount * a.weeks_in_academic_year;
      case "per_day": return amount * a.days_in_academic_year;
      default: return null;
    }
  }
  function fromAY(ay, target, a) {
    var div = { per_academic_year: 1, per_year: 1, per_semester: a.semesters_in_academic_year, per_term: a.terms_in_academic_year, per_month: a.months_in_academic_year }[target];
    return div ? Math.round(ay / div) : null;
  }
  function money(minor) { return "$" + (minor / 100).toLocaleString("en-US", { maximumFractionDigits: 0 }); }

  function calculate(items, target, assumptions) {
    var a = Object.assign({}, DEFAULTS, assumptions || {});
    var res = { target: target, mandatory: 0, optional: 0, deposits: 0, unknown: [], items: [], exclusions: [] };
    items.forEach(function (it) {
      if (it.amount == null || isNaN(it.amount)) { res.unknown.push(it.label); res.items.push({ label: it.label, status: "unknown" }); return; }
      var perPerson = it.amount;
      if (it.basis === "per_unit") {
        if (!a.occupants_per_unit) { res.unknown.push(it.label); res.items.push({ label: it.label, status: "unknown", note: "per-unit price; enter occupants per unit" }); return; }
        perPerson = Math.round(it.amount / a.occupants_per_unit);
      }
      if (it.refundable) { res.deposits += perPerson; res.items.push({ label: it.label, status: "deposit", amount: perPerson }); return; }
      var ay = toAY(perPerson, it.period, a);
      if (ay == null) { res.unknown.push(it.label); res.items.push({ label: it.label, status: "not_convertible" }); return; }
      var conv = it.period === "one_time" ? perPerson : fromAY(ay, target, a);
      if (it.mandatory) res.mandatory += conv; else res.optional += conv;
      res.items.push({ label: it.label, status: it.assumption ? "assumption" : (it.mandatory ? "included" : "optional"), amount: conv });
    });
    return res;
  }
  window.CampusCalc = { calculate: calculate, money: money };

  function readForm(form) {
    var items = [];
    form.querySelectorAll("[data-line]").forEach(function (row) {
      var amountEl = row.querySelector("[data-amount]");
      var raw = amountEl ? amountEl.value.replace(/[$,\s]/g, "") : "";
      var amount = raw === "" ? null : Math.round(parseFloat(raw) * 100);
      var err = row.querySelector(".error");
      if (amountEl) {
        var bad = raw !== "" && (isNaN(amount) || amount < 0);
        amountEl.setAttribute("aria-invalid", bad ? "true" : "false");
        if (err) err.textContent = bad ? "Enter a positive dollar amount, or leave blank for unknown." : "";
        if (bad) amount = null;
      }
      items.push({ label: row.getAttribute("data-label"), amount: amount, period: row.querySelector("[data-period]") ? row.querySelector("[data-period]").value : row.getAttribute("data-period"),
        basis: row.getAttribute("data-basis") || "per_person", mandatory: row.getAttribute("data-mandatory") !== "false", refundable: row.getAttribute("data-refundable") === "true",
        assumption: row.getAttribute("data-assumption") === "true" || (amountEl && amountEl.dataset.userEdited === "true") });
    });
    return items;
  }

  function enhance(form) {
    var out = form.querySelector("[data-result]");
    if (!out) return;
    var targetSel = form.querySelector("[data-target-period]");
    var occ = form.querySelector("[data-occupants]");
    function render() {
      var items = readForm(form);
      var res = calculate(items, targetSel ? targetSel.value : "per_academic_year", { occupants_per_unit: occ && occ.value ? parseInt(occ.value, 10) : null });
      var label = (res.target || "").replace(/_/g, " ");
      var html = '<p class="total">' + money(res.mandatory) + "<small>mandatory charges, " + label + ", per person</small></p>";
      if (res.optional) html += "<p>Optional charges you selected: <b>" + money(res.optional) + "</b> " + label + "</p>";
      if (res.deposits) html += "<p>Refundable deposits (paid up front, not a cost): <b>" + money(res.deposits) + "</b></p>";
      if (res.unknown.length) html += '<p class="value-unknown">Not included because unknown: ' + res.unknown.join(", ") + ". The real total is higher.</p>";
      if (items.some(function (i) { return i.assumption; })) html += '<p class="assumption">Figures you typed are your assumptions, not published facts.</p>';
      out.innerHTML = html;
      out.setAttribute("aria-live", "polite");
    }
    form.addEventListener("input", function (e) { if (e.target && e.target.hasAttribute("data-amount")) e.target.dataset.userEdited = "true"; render(); });
    form.addEventListener("submit", function (e) { e.preventDefault(); render(); });
    render();
  }
  document.querySelectorAll("form[data-calculator]").forEach(enhance);
})();
