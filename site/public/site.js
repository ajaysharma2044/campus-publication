/* Footnote Daily: the little client-side behavior the templates need. Loaded deferred; every page works without it. */
(function () {
  'use strict';
  // DataTable: click a header to sort rows; numeric cells sort as numbers.
  document.querySelectorAll('.dtable').forEach(function (wrap) {
    var table = wrap.querySelector('table'); if (!table) return;
    var tbody = table.tBodies[0]; if (!tbody) return;
    wrap.querySelectorAll('.dtable__sort').forEach(function (btn, i) {
      btn.addEventListener('click', function () {
        var th = btn.closest('th'), idx = Array.prototype.indexOf.call(th.parentNode.children, th);
        var dir = btn.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
        wrap.querySelectorAll('.dtable__sort').forEach(function (b) { b.removeAttribute('aria-sort'); });
        btn.setAttribute('aria-sort', dir);
        var rows = Array.prototype.slice.call(tbody.rows);
        var num = function (s) { var n = parseFloat(String(s).replace(/[^0-9.\-]/g, '')); return isNaN(n) ? null : n; };
        rows.sort(function (a, b) {
          var x = a.cells[idx] ? a.cells[idx].textContent.trim() : '', y = b.cells[idx] ? b.cells[idx].textContent.trim() : '';
          var nx = num(x), ny = num(y), r;
          if (nx !== null && ny !== null && /\d/.test(x) && /\d/.test(y)) r = nx - ny; else r = x.localeCompare(y, undefined, { numeric: true, sensitivity: 'base' });
          return dir === 'ascending' ? r : -r;
        });
        rows.forEach(function (r) { tbody.appendChild(r); });
      });
    });
  });

  // Reader feedback: with script, a "No, I still need..." button reveals the textarea and its Send button.
  var fb = document.querySelector('.feedback__form');
  if (fb) {
    var noBtn = fb.querySelector('[data-feedback-no]'), need = fb.querySelector('[data-feedback-need]');
    if (noBtn && need) {
      need.hidden = true; noBtn.hidden = false;
      noBtn.addEventListener('click', function () { need.hidden = false; noBtn.setAttribute('aria-expanded', 'true'); noBtn.hidden = true; var t = need.querySelector('textarea'); if (t) t.focus(); });
    }
  }

  // Search page: Pagefind's static index rendered as GuideList rows with our own pagination.
  var search = document.querySelector('[data-search]');
  if (search) {
    var input = search.querySelector('.search__input'), count = search.querySelector('[data-count]'), list = search.querySelector('[data-results]'), pager = search.querySelector('[data-pager]');
    var PER = 10, pf = null, page = 1, results = [];
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function render() {
      var total = results.length, pages = Math.max(1, Math.ceil(total / PER));
      count.textContent = total ? total + (total === 1 ? ' result' : ' results') + ' for “' + input.value + '”' : (input.value ? 'No results for “' + input.value + '”. Try a shorter query, or browse the Cornell guide.' : '');
      var slice = results.slice((page - 1) * PER, page * PER);
      Promise.all(slice.map(function (r) { return r.data(); })).then(function (items) {
        list.innerHTML = items.map(function (d) {
          var cat = (d.meta && d.meta.category) || '';
          return '<li class="glist__item">' + (cat ? '<p class="glist__kicker">' + esc(cat) + '</p>' : '') + '<h2 class="glist__title"><a href="' + esc(d.url) + '">' + esc(d.meta.title || d.url) + '</a></h2><p class="glist__dek">' + (d.excerpt || '') + '</p></li>';
        }).join('');
        var html = '';
        if (pages > 1) { for (var p = 1; p <= pages; p++) html += p === page ? '<li><span aria-current="page">' + p + '</span></li>' : '<li><a href="#p' + p + '" data-page="' + p + '">' + p + '</a></li>'; }
        pager.innerHTML = html;
      });
    }
    pager.addEventListener('click', function (e) { var a = e.target.closest('[data-page]'); if (!a) return; e.preventDefault(); page = +a.getAttribute('data-page'); render(); window.scrollTo(0, 0); });
    function run(q) {
      if (!q) { results = []; render(); return; }
      var load = pf ? Promise.resolve(pf) : import('/pagefind/pagefind.js').then(function (m) { pf = m; return m.init && m.init(), m; }).catch(function () { return null; });
      load.then(function (m) {
        if (!m) { count.textContent = 'Search is available on the built site (the index is generated at build time).'; return; }
        m.search(q).then(function (res) { results = res.results; page = 1; render(); });
      });
    }
    var params = new URLSearchParams(location.search), q = params.get('q') || '';
    if (q) { input.value = q; run(q); }
    search.querySelector('form').addEventListener('submit', function (e) { e.preventDefault(); var v = input.value.trim(); history.replaceState(null, '', v ? '?q=' + encodeURIComponent(v) : location.pathname); run(v); });
  }
})();
