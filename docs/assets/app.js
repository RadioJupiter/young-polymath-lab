/* Progress (localStorage only: no accounts, no network, no tracking), Today view, timetable, progress page. */
(function () {
  var S = window.SCHOOL || { days: [], timetable: { rows: [], days: [] }, key: "school" };
  var KEY = S.key + ":done", START = S.key + ":start";
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function save(d) { localStorage.setItem(KEY, JSON.stringify(d)); }
  var done = load();
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function wire(root) {
    (root || document).querySelectorAll("input[data-done]").forEach(function (b) {
      b.checked = !!done[b.dataset.done];
      b.addEventListener("change", function () {
        done = load();
        if (b.checked) done[b.dataset.done] = new Date().toISOString().slice(0, 10); else delete done[b.dataset.done];
        save(done);
        document.querySelectorAll('input[data-done="' + b.dataset.done + '"]').forEach(function (o) { o.checked = b.checked; });
        refreshCounts();
      });
    });
  }
  function refreshCounts() {
    document.querySelectorAll("[data-count]").forEach(function (c) {
      var day = S.days.find(function (d) { return d.id === c.dataset.count; });
      if (!day) return;
      var n = day.sections.filter(function (s) { return done[s.id]; }).length;
      c.textContent = n + " / " + day.sections.length;
    });
    var t = document.getElementById("total-count");
    if (t) {
      var all = 0, got = 0;
      S.days.forEach(function (d) { d.sections.forEach(function (s) { all++; if (done[s.id]) got++; }); });
      t.textContent = got + " of " + all + " lessons complete";
    }
  }
  var root = document.body.dataset.root || "";
  var WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  function timetableTable(onlyDay) {
    var T = S.timetable, tbl = el("table", { "class": "timetable" }), head = el("tr");
    head.appendChild(el("th", {}, "Time"));
    T.days.forEach(function (d, i) { if (onlyDay == null || onlyDay === i) head.appendChild(el("th", {}, d)); });
    tbl.appendChild(head);
    T.rows.forEach(function (r) {
      var tr = el("tr", r.break ? { "class": "break" } : {});
      tr.appendChild(el("td", { "class": "time" }, r.time));
      r.cells.forEach(function (c, i) { if (onlyDay == null || onlyDay === i) tr.appendChild(el("td", {}, c)); });
      tbl.appendChild(tr);
    });
    return tbl;
  }
  var tt = document.getElementById("timetable-root");
  if (tt) tt.appendChild(timetableTable(null));

  function schoolDayIndex(start, date) {
    // Count weekdays from start to date inclusive; returns 1-based index or 0 if date is before start.
    var d = new Date(start.getTime()), n = 0;
    if (date < start) return 0;
    while (d <= date) { var w = d.getDay(); if (w !== 0 && w !== 6) n++; d.setDate(d.getDate() + 1); }
    return n;
  }
  function parseISO(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }

  var today = document.getElementById("today-root");
  if (today) {
    var startIn = document.getElementById("start-date"), shift = 0;
    var stored = localStorage.getItem(START);
    if (stored) startIn.value = stored;
    startIn.addEventListener("change", function () { localStorage.setItem(START, startIn.value); shift = 0; render(); });
    document.getElementById("prev-day").addEventListener("click", function () { shift--; render(); });
    document.getElementById("next-day").addEventListener("click", function () { shift++; render(); });
    document.getElementById("this-day").addEventListener("click", function () { shift = 0; render(); });
    function render() {
      today.innerHTML = "";
      var now = new Date(); now.setHours(0, 0, 0, 0);
      var label = el("p", { "class": "date" }, now.toLocaleDateString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric" }));
      today.appendChild(label);
      if (!startIn.value) { today.appendChild(el("p", { "class": "note" }, "Set the first day of term above. The schedule counts school days (Monday to Friday) from that date.")); return; }
      var start = parseISO(startIn.value), wk = now.getDay(), idx = schoolDayIndex(start, now);
      if (wk === 0 || wk === 6) { today.appendChild(el("p", { "class": "note" }, "No lessons today. Showing the next school day.")); idx = idx + 1; }
      idx = Math.max(1, idx + shift);
      var week = Math.ceil(idx / 5), dow = (idx - 1) % 5;
      today.appendChild(el("h2", {}, "School day " + idx + " · Week " + week + ", " + S.timetable.days[dow]));
      var day = S.days[idx - 1];
      if (!day) {
        var p = el("p", { "class": "note" });
        p.innerHTML = "Day " + idx + " is beyond the lessons written so far (" + S.days.length + " days). Follow the <a href='" + root + "scope.html'>scope and sequence</a> for this week's topics.";
        today.appendChild(p);
      } else {
        var h = el("h3"); var a = el("a", { href: root + "days/" + day.id + ".html" }, day.title); h.appendChild(a); today.appendChild(h);
        var ul = el("ul", { "class": "checklist" });
        day.sections.forEach(function (s) {
          var li = el("li"), lab = el("label"), cb = el("input", { type: "checkbox", "data-done": s.id });
          lab.appendChild(cb);
          var link = el("a", { href: root + "days/" + day.id + ".html#" + s.id.slice(day.id.length + 1) }, " " + s.name);
          lab.appendChild(link); li.appendChild(lab); ul.appendChild(li);
        });
        today.appendChild(ul);
        var kp = el("p"); kp.appendChild(el("a", { href: root + "keys/" + day.id + ".html" }, "Answer keys for this day")); today.appendChild(kp);
      }
      today.appendChild(el("h3", {}, "Timetable"));
      today.appendChild(timetableTable(dow));
      wire(today);
    }
    render();
  }

  var prog = document.getElementById("progress-root");
  if (prog) {
    prog.appendChild(el("p", { id: "total-count", "class": "total" }));
    S.days.forEach(function (d) {
      var box = el("details", { "class": "progress-day" }), sum = el("summary");
      sum.appendChild(el("a", { href: root + "days/" + d.id + ".html" }, d.title));
      sum.appendChild(el("span", { "class": "count", "data-count": d.id }));
      box.appendChild(sum);
      var ul = el("ul", { "class": "checklist" });
      d.sections.forEach(function (s) {
        var li = el("li"), lab = el("label");
        lab.appendChild(el("input", { type: "checkbox", "data-done": s.id }));
        lab.appendChild(document.createTextNode(" " + s.name + (done[s.id] ? "  (" + done[s.id] + ")" : "")));
        li.appendChild(lab); ul.appendChild(li);
      });
      box.appendChild(ul); prog.appendChild(box);
    });
    var tools = el("p", { "class": "tools" });
    var exp = el("button", { type: "button" }, "Export progress (JSON)");
    exp.addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(load(), null, 2)], { type: "application/json" });
      var a = el("a", { href: URL.createObjectURL(blob), download: "progress.json" }); a.click();
    });
    var imp = el("input", { type: "file", accept: "application/json", "aria-label": "Import progress" });
    imp.addEventListener("change", function () {
      var r = new FileReader(); r.onload = function () { try { save(JSON.parse(r.result)); location.reload(); } catch (e) { alert("That file is not a progress export."); } };
      r.readAsText(imp.files[0]);
    });
    var rst = el("button", { type: "button" }, "Clear all progress");
    rst.addEventListener("click", function () { if (confirm("Clear every checkmark on this device?")) { save({}); location.reload(); } });
    tools.appendChild(exp); tools.appendChild(document.createTextNode(" Import: ")); tools.appendChild(imp); tools.appendChild(rst);
    prog.appendChild(tools);
  }
  wire(document);
  refreshCounts();
})();
