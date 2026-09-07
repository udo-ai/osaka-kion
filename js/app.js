/* 大阪市の気温グラフ 描画スクリプト
 * データは js/data.js（window.KION_DATA）から読み込む。
 * KION_DATA = { "2016": {year, months:[{month, avg[], max[], min[]}, ...]}, ... }
 */
(function () {
  "use strict";

  var YEARS = Object.keys(window.KION_DATA).map(Number).sort(function (a, b) { return a - b; });
  var charts = []; // 破棄用に保持

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function colors() {
    return {
      max: cssVar("--series-max"),
      min: cssVar("--series-min"),
      nmax: cssVar("--series-nmax"),
      nmin: cssVar("--series-nmin"),
      grid: cssVar("--grid"),
      muted: cssVar("--muted"),
      surface: cssVar("--surface"),
      ink: cssVar("--ink")
    };
  }

  function makeDataset(label, values, color, dashed) {
    return {
      label: label,
      data: values,
      borderColor: color,
      backgroundColor: color,
      borderWidth: dashed ? 1.5 : 2,
      borderDash: dashed ? [5, 4] : [],
      pointRadius: 0,
      pointHoverRadius: dashed ? 3 : 4,
      tension: 0.25,
      spanGaps: true
    };
  }

  function renderMonth(container, yearData, monthIndex) {
    var m = yearData.months[monthIndex];
    var c = colors();
    var days = m.max.map(function (_, i) { return i + 1; });
    // 平年値（1991〜2020年平均）。2月は月の日数（28日/29日）に合わせて切り詰める
    var normals = window.KION_NORMALS.months[monthIndex];
    var nmax = normals.nmax.slice(0, m.max.length);
    var nmin = normals.nmin.slice(0, m.min.length);

    var card = document.createElement("div");
    card.className = "chart-card";
    var title = document.createElement("h3");
    title.textContent = yearData.year + "年" + m.month + "月";
    var wrap = document.createElement("div");
    wrap.className = "canvas-wrap";
    var canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label",
      yearData.year + "年" + m.month + "月の大阪市の日別の最高気温・最低気温と平年値の折れ線グラフ");
    wrap.appendChild(canvas);
    card.appendChild(title);
    card.appendChild(wrap);
    container.appendChild(card);

    var chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: days,
        datasets: [
          makeDataset("最高気温", m.max, c.max, false),
          makeDataset("最低気温", m.min, c.min, false),
          makeDataset("最高気温の平年値", nmax, c.nmax, true),
          makeDataset("最低気温の平年値", nmin, c.nmin, true)
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false }, // 凡例はページ上部に共通表示
          tooltip: {
            backgroundColor: c.surface,
            titleColor: c.ink,
            bodyColor: c.ink,
            borderColor: c.grid,
            borderWidth: 1,
            callbacks: {
              title: function (items) {
                return m.month + "月" + items[0].label + "日";
              },
              label: function (item) {
                var v = item.parsed.y;
                return item.dataset.label + ": " + (v === null ? "―" : v.toFixed(1) + "℃");
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: c.grid, drawTicks: false },
            border: { display: false },
            ticks: {
              color: c.muted,
              font: { size: 10 },
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 8
            }
          },
          y: {
            min: -5,
            max: 40,
            grid: { color: c.grid, drawTicks: false },
            border: { display: false },
            ticks: {
              color: c.muted,
              font: { size: 10 },
              stepSize: 5,
              callback: function (v) { return v + "℃"; }
            }
          }
        }
      }
    });
    charts.push(chart);
  }

  function avg(values) {
    var nums = values.filter(function (v) { return v !== null; });
    if (!nums.length) return null;
    var sum = nums.reduce(function (a, b) { return a + b; }, 0);
    return sum / nums.length;
  }

  function fmt(v) { return v === null ? "―" : v.toFixed(1) + "℃"; }

  function renderSummary(yearData) {
    var tbody = document.querySelector("#summaryTable tbody");
    tbody.innerHTML = "";
    yearData.months.forEach(function (m) {
      var maxNums = m.max.filter(function (v) { return v !== null; });
      var minNums = m.min.filter(function (v) { return v !== null; });
      var tr = document.createElement("tr");
      var cells = [
        m.month + "月",
        fmt(avg(m.max)),
        fmt(avg(m.min)),
        maxNums.length ? fmt(Math.max.apply(null, maxNums)) : "―",
        minNums.length ? fmt(Math.min.apply(null, minNums)) : "―"
      ];
      cells.forEach(function (text, i) {
        var cell = document.createElement(i === 0 ? "th" : "td");
        if (i === 0) cell.setAttribute("scope", "row");
        cell.textContent = text;
        tr.appendChild(cell);
      });
      tbody.appendChild(tr);
    });
  }

  function renderYear(year) {
    var yearData = window.KION_DATA[String(year)];
    document.getElementById("yearHeading").textContent = year + "年の気温（月別）";
    var grid = document.getElementById("chartGrid");
    charts.forEach(function (ch) { ch.destroy(); });
    charts = [];
    grid.innerHTML = "";
    yearData.months.forEach(function (m, i) {
      // データがまだ無い月（今年の未来月など）は表示しない
      if (m.max.length) renderMonth(grid, yearData, i);
    });
    renderSummary(yearData);
    document.querySelectorAll(".year-tabs button").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.dataset.year === String(year) ? "true" : "false");
    });
  }

  function buildTabs() {
    var nav = document.getElementById("yearTabs");
    YEARS.forEach(function (year) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = year + "年";
      btn.dataset.year = String(year);
      btn.setAttribute("aria-pressed", "false");
      btn.addEventListener("click", function () { renderYear(year); });
      nav.appendChild(btn);
    });
  }

  // ダークモード切替時にグラフの色を描き直す
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
    var current = document.querySelector('.year-tabs button[aria-pressed="true"]');
    if (current) renderYear(Number(current.dataset.year));
  });

  // 「一言比較」ボックス（js/today.js があるときだけ表示）
  function renderToday() {
    var t = window.KION_TODAY;
    if (!t) return;
    var box = document.getElementById("todayBox");
    function sign(v) { return (v > 0 ? "+" : "") + v.toFixed(1); }
    box.innerHTML =
      '<span class="today-date">' + t.label + "（" + t.weekday + "）の大阪</span>" +
      '<span class="today-item"><i class="swatch swatch-max"></i>最高 ' + t.tmax.toFixed(1) +
      "℃（平年比 " + sign(t.dmax) + "℃）</span>" +
      '<span class="today-item"><i class="swatch swatch-min"></i>最低 ' + t.tmin.toFixed(1) +
      "℃（平年比 " + sign(t.dmin) + "℃）</span>";
    box.hidden = false;
  }

  buildTabs();
  renderToday();
  renderYear(YEARS[YEARS.length - 1]); // 初期表示は最新年
})();
