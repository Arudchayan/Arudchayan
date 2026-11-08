/* ==========================================================================
   PokéLab dashboard
   Dependency-free data loading + SVG chart rendering.
   ========================================================================== */

(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const REPORT_COMMAND = "python -m pokerl report";
  const DATA_PATHS = {
    leaderboard: "results/leaderboard.json",
    learning: "results/learning_curve.json",
    generalization: "results/generalization.json",
  };
  const DATASET_FILES = {
    leaderboard: "leaderboard.json",
    learning: "learning_curve.json",
    generalization: "generalization.json",
  };
  const PALETTE = [
    "#c9a96a",
    "#7f9cc4",
    "#8fae8b",
    "#c98d7a",
    "#a48cb8",
    "#7fa8a8",
    "#c2a3a3",
    "#9aa0a6",
  ];
  const LEARNING_CHARTS = [
    {
      key: "bc",
      containerId: "bc-chart",
      metricId: "bc-final",
      seriesName: "Behaviour cloning",
      xAxisLabel: "Samples",
      color: "#c9a96a",
      chartTitle: "Behaviour cloning learning curve",
      chartDescription:
        "Line chart of evaluation win rate as the number of behaviour-cloning samples increases.",
      emptyTitle: "No behaviour-cloning checkpoints",
      emptyMessage: "This report contains no behaviour-cloning samples.",
      emptyHint: "Expected bc[] entries with samples and win_rate.",
    },
    {
      key: "rl",
      containerId: "rl-chart",
      metricId: "rl-final",
      seriesName: "Reinforce",
      xAxisLabel: "Episodes",
      color: "#7f9cc4",
      chartTitle: "Reinforce learning curve",
      chartDescription:
        "Line chart of evaluation win rate as the number of reinforcement-learning episodes increases.",
      emptyTitle: "No reinforce checkpoints",
      emptyMessage: "This report contains no reinforce evaluation checkpoints.",
      emptyHint: "Expected rl[] entries with episode and win_rate.",
    },
  ];

  const state = {
    leaderboard: { status: "loading", rows: [], matches: [], hasMatches: false, rawCount: 0 },
    learning: { status: "loading", bc: [], rl: [] },
    generalization: { status: "loading", rows: [], rawCount: 0 },
  };

  let chartSequence = 0;
  let copyResetTimer = 0;

  /* ------------------------------------------------------------------------
     Small utilities
     ------------------------------------------------------------------------ */

  function $(selector, root = document) {
    return root.querySelector(selector);
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function svgElement(tag, attributes = {}) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attributes)) {
      if (value !== undefined && value !== null) node.setAttribute(key, String(value));
    }
    return node;
  }

  function svgText(parent, attributes, text) {
    const node = svgElement("text", attributes);
    node.textContent = text;
    parent.appendChild(node);
    return node;
  }

  function setText(id, text) {
    const node = document.getElementById(id);
    if (!node) return null;
    node.textContent = text;
    return node;
  }

  function setMetric(id, text, title) {
    const node = setText(id, text);
    if (!node) return;
    if (title) node.title = title;
    else node.removeAttribute("title");
  }

  function clamp(value, low, high) {
    return Math.min(high, Math.max(low, value));
  }

  function debounce(fn, delay) {
    let timer = 0;
    return (...args) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn(...args), delay);
    };
  }

  function toNumber(value) {
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    if (typeof value === "string" && value.trim() !== "") {
      const cleaned = value.replace(/,/g, "").replace(/%/g, "").trim();
      const parsed = Number(cleaned);
      return Number.isFinite(parsed) ? parsed : null;
    }
    return null;
  }

  function firstFinite(...values) {
    for (const value of values) {
      const parsed = toNumber(value);
      if (parsed !== null) return parsed;
    }
    return null;
  }

  function firstNonEmptyString(...values) {
    for (const value of values) {
      if (typeof value === "string" && value.trim()) return value.trim();
    }
    return "";
  }

  function normalizeRate(value) {
    if (typeof value === "string" && value.trim().endsWith("%")) {
      const parsed = toNumber(value);
      return parsed === null ? null : clamp(parsed / 100, 0, 1);
    }
    const parsed = toNumber(value);
    if (parsed === null) return null;
    const rate = parsed > 1.0000001 && parsed <= 100 ? parsed / 100 : parsed;
    return clamp(rate, 0, 1);
  }

  function normalizeInterval(value) {
    let low;
    let high;
    if (Array.isArray(value)) {
      low = value[0];
      high = value[1];
    } else if (value && typeof value === "object") {
      low = value.low ?? value.lower ?? value[0];
      high = value.high ?? value.upper ?? value[1];
    }
    const lo = normalizeRate(low);
    const hi = normalizeRate(high);
    if (lo === null || hi === null) return null;
    return lo <= hi ? [lo, hi] : [hi, lo];
  }

  function wilsonInterval(wins, games) {
    if (!Number.isFinite(wins) || !Number.isFinite(games) || games <= 0) return null;
    const z = 1.959963984540054;
    const p = clamp(wins / games, 0, 1);
    const denominator = 1 + (z * z) / games;
    const centre = (p + (z * z) / (2 * games)) / denominator;
    const margin =
      (z * Math.sqrt((p * (1 - p) + (z * z) / (4 * games)) / games)) / denominator;
    return [clamp(centre - margin, 0, 1), clamp(centre + margin, 0, 1)];
  }

  function niceStep(rawStep) {
    if (!Number.isFinite(rawStep) || rawStep <= 0) return 1;
    const power = 10 ** Math.floor(Math.log10(rawStep));
    const fraction = rawStep / power;
    const niceFraction = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10;
    return niceFraction * power;
  }

  function cleanNumber(value) {
    return Number(value.toPrecision(12));
  }

  function niceScale(min, max, targetTicks = 4) {
    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      return { min: 0, max: 1, ticks: [0, 0.5, 1] };
    }
    if (min === max) {
      const padding = Math.abs(min) * 0.1 || 1;
      min -= padding;
      max += padding;
    }
    if (min > max) [min, max] = [max, min];
    const step = niceStep((max - min) / Math.max(2, targetTicks));
    const niceMin = Math.floor(min / step) * step;
    const niceMax = Math.ceil(max / step) * step;
    const count = Math.max(1, Math.round((niceMax - niceMin) / step));
    const ticks = [];
    for (let i = 0; i <= count; i += 1) ticks.push(cleanNumber(niceMin + i * step));
    return { min: cleanNumber(niceMin), max: cleanNumber(niceMax), ticks };
  }

  function logTicks(min, max, targetTicks = 5) {
    if (!(min > 0) || !(max > min)) return [min, max];
    const ticks = [];
    for (let exponent = Math.floor(Math.log10(min)); exponent <= Math.ceil(Math.log10(max)); exponent += 1) {
      for (const multiplier of [1, 2, 5]) {
        const value = multiplier * 10 ** exponent;
        if (value >= min * 0.999 && value <= max * 1.001) ticks.push(cleanNumber(value));
      }
    }
    if (ticks.length < 2) return [cleanNumber(min), cleanNumber(max)];
    if (ticks.length > targetTicks + 2) {
      const stride = Math.ceil(ticks.length / targetTicks);
      return ticks.filter((_, index) => index % stride === 0 || index === ticks.length - 1);
    }
    return ticks;
  }

  function buildXScale(values, targetTicks = 5) {
    const valid = values.filter((value) => Number.isFinite(value));
    if (!valid.length) return { min: 0, max: 1, ticks: [0, 0.5, 1], log: false };
    const min = Math.min(...valid);
    const max = Math.max(...valid);
    const allPositive = valid.every((value) => value > 0);
    const useLog = allPositive && valid.length > 1 && max / min >= 18;
    if (useLog) {
      const low = Math.max(min * 0.85, Number.MIN_VALUE);
      const high = max * 1.18;
      const ticks = logTicks(low, high, targetTicks);
      return {
        min: Math.min(low, ticks[0] ?? low),
        max: Math.max(high, ticks[ticks.length - 1] ?? high),
        ticks,
        log: true,
      };
    }
    const span = max - min;
    const padding = span > 0 ? span * 0.12 : Math.max(1, Math.abs(max) * 0.12);
    const scale = niceScale(min - padding, max + padding, targetTicks);
    return { ...scale, log: false };
  }

  function projectX(value, scale, left, width) {
    let ratio;
    if (scale.log && scale.min > 0) {
      ratio =
        (Math.log10(Math.max(value, Number.MIN_VALUE)) - Math.log10(scale.min)) /
        (Math.log10(scale.max) - Math.log10(scale.min));
    } else {
      ratio = (value - scale.min) / (scale.max - scale.min || 1);
    }
    return left + clamp(ratio, 0, 1) * width;
  }

  function projectY(value, min, max, top, height) {
    const ratio = (value - min) / (max - min || 1);
    return top + (1 - clamp(ratio, 0, 1)) * height;
  }

  function truncateText(value, maxLength) {
    const text = String(value);
    if (text.length <= maxLength) return text;
    return `${text.slice(0, Math.max(1, maxLength - 1))}…`;
  }

  function trimFixed(value, digits) {
    const fixed = value.toFixed(digits);
    return fixed.includes(".") ? fixed.replace(/\.?0+$/, "") : fixed;
  }

  function formatInteger(value) {
    return Math.round(value).toLocaleString("en-US");
  }

  function pluralCount(value, singular, plural = `${singular}s`) {
    return `${formatInteger(value)} ${value === 1 ? singular : plural}`;
  }

  function formatCompact(value) {
    if (!Number.isFinite(value)) return "—";
    const absolute = Math.abs(value);
    if (absolute >= 1e9) return `${trimFixed(value / 1e9, 1)}B`;
    if (absolute >= 1e6) return `${trimFixed(value / 1e6, 1)}M`;
    if (absolute >= 1e3) return `${trimFixed(value / 1e3, 1)}k`;
    if (absolute >= 100) return formatInteger(value);
    if (absolute >= 10) return trimFixed(value, 1);
    if (absolute >= 1) return trimFixed(value, 2);
    if (absolute === 0) return "0";
    return trimFixed(value, 2);
  }

  function formatElo(value) {
    if (!Number.isFinite(value)) return "—";
    const rounded = Math.round(value * 10) / 10;
    return rounded.toLocaleString("en-US", {
      minimumFractionDigits: Number.isInteger(rounded) ? 0 : 1,
      maximumFractionDigits: 1,
    });
  }

  function formatPercent(value, digits = 1) {
    if (!Number.isFinite(value)) return "—";
    return `${(clamp(value, 0, 1) * 100).toFixed(digits)}%`;
  }

  function formatPercentPoints(value) {
    if (!Number.isFinite(value)) return "—";
    const points = value * 100;
    const sign = points > 0.05 ? "+" : points < -0.05 ? "−" : "";
    return `${sign}${Math.abs(points).toFixed(1)} pp`;
  }

  function formatDecisionsPerSecond(value) {
    if (!Number.isFinite(value)) return "—";
    if (value >= 1000) return `${trimFixed(value / 1000, 1)}k`;
    if (value >= 100) return formatInteger(value);
    if (value >= 10) return trimFixed(value, 1);
    return trimFixed(value, 2);
  }

  function formatInterval(interval) {
    if (!interval) return "—";
    return `${formatPercent(interval[0]).replace("%", "")}–${formatPercent(interval[1])}`;
  }

  function dataHint(datasetKey) {
    if (window.location.protocol === "file:") {
      return "Fetch is blocked on file://. Serve docs/ with: python -m http.server -d docs 8000";
    }
    return `Expected at results/${DATASET_FILES[datasetKey]} (relative to docs/).`;
  }

  /* ------------------------------------------------------------------------
     Dataset normalization
     ------------------------------------------------------------------------ */

  function aggregateDecisionsPerSecond(matches, agentName) {
    let weightedTotal = 0;
    let totalWeight = 0;
    for (const match of matches) {
      if (!match || typeof match !== "object") continue;
      const a = firstNonEmptyString(match.agent_a, match.agentA, match.agent_a_name);
      const b = firstNonEmptyString(match.agent_b, match.agentB, match.agent_b_name);
      if (a !== agentName && b !== agentName) continue;

      let dps = firstFinite(match.decisions_per_sec, match.decisionsPerSec, match.dps);
      if (dps === null) {
        const decisions = firstFinite(match.decisions, match.total_decisions);
        const elapsed = firstFinite(match.elapsed_s, match.elapsed_seconds, match.elapsed);
        if (decisions !== null && elapsed !== null && elapsed > 0) dps = decisions / elapsed;
      }
      if (dps === null || dps < 0) continue;

      const games = firstFinite(match.games, match.total_games);
      const weight = games !== null && games > 0 ? games : 1;
      weightedTotal += dps * weight;
      totalWeight += weight;
    }
    return totalWeight > 0 ? weightedTotal / totalWeight : null;
  }

  function normalizeLeaderboard(data) {
    const rawStandings = Array.isArray(data?.standings) ? data.standings : [];
    const matches = Array.isArray(data?.matches)
      ? data.matches.filter((match) => match && typeof match === "object")
      : [];
    const hasMatches = Array.isArray(data?.matches);

    const rows = rawStandings
      .filter((standing) => standing && typeof standing === "object")
      .map((standing, index) => {
        const agent =
          firstNonEmptyString(standing.agent, standing.name, standing.agent_name) || `Agent ${index + 1}`;
        const rating = firstFinite(standing.rating, standing.elo, standing.elo_rating);
        const wins = firstFinite(standing.wins);
        const losses = firstFinite(standing.losses);
        const draws = firstFinite(standing.draws);
        const decisive = wins !== null && losses !== null ? wins + losses : null;
        const hasRecord = wins !== null && losses !== null && draws !== null;

        let winRate = normalizeRate(standing.win_rate ?? standing.winRate);
        if (winRate === null && decisive !== null && decisive > 0) winRate = clamp(wins / decisive, 0, 1);

        let interval = normalizeInterval(
          standing.ci95 ?? standing.ci_95 ?? standing.ci ?? standing.confidence_interval,
        );
        if (!interval && decisive !== null && decisive > 0) interval = wilsonInterval(wins, decisive);

        const directDps = firstFinite(
          standing.decisions_per_sec,
          standing.decisionsPerSec,
          standing.dps,
        );
        const dps = directDps !== null ? directDps : aggregateDecisionsPerSecond(matches, agent);

        return {
          agent,
          rating,
          wins,
          losses,
          draws,
          hasRecord,
          winRate,
          interval,
          dps,
          originalIndex: index,
        };
      });

    rows.sort((a, b) => {
      if (a.rating !== null && b.rating !== null) return b.rating - a.rating;
      if (a.rating !== null) return -1;
      if (b.rating !== null) return 1;
      const aRate = a.winRate ?? -1;
      const bRate = b.winRate ?? -1;
      return bRate - aRate || a.agent.localeCompare(b.agent);
    });
    rows.forEach((row, index) => {
      row.rank = index + 1;
    });

    return { rows, matches, hasMatches, rawCount: rawStandings.length };
  }

  function normalizeLearning(data) {
    const makeSeries = (list, xKeys) => {
      if (!Array.isArray(list)) return [];
      return list
        .filter((entry) => entry && typeof entry === "object")
        .map((entry) => ({
          x: firstFinite(...xKeys.map((key) => entry[key])),
          y: normalizeRate(entry.win_rate ?? entry.winRate),
          raw: entry,
        }))
        .filter((entry) => entry.x !== null && entry.y !== null)
        .sort((a, b) => a.x - b.x);
    };

    return {
      bc: makeSeries(data?.bc, ["samples", "sample_count", "examples"]),
      rl: makeSeries(data?.rl, ["episode", "episodes", "step"]),
    };
  }

  function normalizeGeneralization(data) {
    const rawResults = Array.isArray(data?.results) ? data.results : [];
    const rows = rawResults
      .filter((entry) => entry && typeof entry === "object")
      .map((entry, index) => {
        const agent =
          firstNonEmptyString(entry.agent, entry.name, entry.agent_name) || `Agent ${index + 1}`;
        const train = normalizeRate(
          entry.train_win_rate ?? entry.trainWinRate ?? entry.train_rate,
        );
        const heldOut = normalizeRate(
          entry.heldout_win_rate ??
            entry.held_out_win_rate ??
            entry.heldOutWinRate ??
            entry.heldout_rate,
        );
        return {
          agent,
          train,
          heldOut,
          gap: train !== null && heldOut !== null ? heldOut - train : null,
          originalIndex: index,
        };
      })
      .filter((row) => row.train !== null || row.heldOut !== null);

    rows.sort((a, b) => {
      const aValue = a.heldOut ?? a.train ?? -1;
      const bValue = b.heldOut ?? b.train ?? -1;
      return bValue - aValue || a.agent.localeCompare(b.agent);
    });

    return { rows, rawCount: rawResults.length };
  }

  /* ------------------------------------------------------------------------
     Fetching
     ------------------------------------------------------------------------ */

  async function fetchJSON(path) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(path, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
      const data = await response.json();
      if (!data || typeof data !== "object" || Array.isArray(data)) {
        throw new Error(`${path}: expected a JSON object`);
      }
      return data;
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function loadLeaderboard() {
    const dataset = state.leaderboard;
    try {
      const data = await fetchJSON(DATA_PATHS.leaderboard);
      const normalized = normalizeLeaderboard(data);
      Object.assign(dataset, normalized, { status: "ready" });
      renderLeaderboard();
    } catch (error) {
      dataset.status = "error";
      console.warn("[PokéLab] Could not load leaderboard data.", error);
      renderLeaderboardFailure();
    }
  }

  async function loadLearning() {
    const dataset = state.learning;
    try {
      const data = await fetchJSON(DATA_PATHS.learning);
      Object.assign(dataset, normalizeLearning(data), { status: "ready" });
      renderLearning();
    } catch (error) {
      dataset.status = "error";
      console.warn("[PokéLab] Could not load learning-curve data.", error);
      renderLearningFailure();
    }
  }

  async function loadGeneralization() {
    const dataset = state.generalization;
    try {
      const data = await fetchJSON(DATA_PATHS.generalization);
      Object.assign(dataset, normalizeGeneralization(data), { status: "ready" });
      renderGeneralization();
    } catch (error) {
      dataset.status = "error";
      console.warn("[PokéLab] Could not load generalization data.", error);
      renderGeneralizationFailure();
    }
  }

  function finalizeBanner() {
    const allFailed = ["leaderboard", "learning", "generalization"].every(
      (key) => state[key].status === "error",
    );
    const banner = document.getElementById("data-banner");
    if (!banner) return;
    banner.hidden = !allFailed;

    if (allFailed) {
      const hint = document.getElementById("data-banner-hint");
      if (hint) {
        hint.hidden = false;
        hint.textContent =
          window.location.protocol === "file:"
            ? "file:// blocks data fetches. Serve the site with: python -m http.server -d docs 8000"
            : "Expected docs/results/*.json. Serve the site over HTTP and refresh.";
      }
    }
  }

  /* ------------------------------------------------------------------------
     Shared DOM pieces
     ------------------------------------------------------------------------ */

  function setDatasetTag(id, text, tone = "live") {
    const node = document.getElementById(id);
    if (!node) return;
    node.replaceChildren();
    const dot = element("span", "dataset-tag__dot");
    dot.setAttribute("aria-hidden", "true");
    node.appendChild(dot);
    node.appendChild(document.createTextNode(text));
    if (tone === "unavailable") node.dataset.state = "unavailable";
    else delete node.dataset.state;
  }

  function renderEmptyState(
    target,
    {
      title = "No results yet",
      message = "The benchmark data is not available in this checkout.",
      showCommand = true,
      hint = "",
    } = {},
  ) {
    if (!target) return;
    target.replaceChildren();
    const wrapper = element("div", "empty-state");
    const glyph = element("span", "empty-state__glyph", "∅");
    glyph.setAttribute("aria-hidden", "true");
    wrapper.appendChild(glyph);
    wrapper.appendChild(element("h4", "", title));
    wrapper.appendChild(element("p", "", message));

    if (showCommand) {
      const commandLine = element("p", "empty-command");
      const command = element("code", "", REPORT_COMMAND);
      commandLine.appendChild(command);
      wrapper.appendChild(commandLine);
    }
    if (hint) wrapper.appendChild(element("p", "empty-state__hint", hint));

    target.appendChild(wrapper);
  }

  function chartWidth(container, minimum = 250) {
    if (!container) return 600;
    const style = window.getComputedStyle(container);
    const paddingLeft = Number.parseFloat(style.paddingLeft) || 0;
    const paddingRight = Number.parseFloat(style.paddingRight) || 0;
    const measured = container.clientWidth - paddingLeft - paddingRight;
    return Math.max(minimum, Math.round(measured > 0 ? measured : 600));
  }

  function createChart(container, width, height, titleText, descriptionText) {
    container.replaceChildren();
    const sequence = (chartSequence += 1);
    const uid = `pkl-chart-${sequence}`;
    const svg = svgElement("svg", {
      class: "chart-svg",
      viewBox: `0 0 ${width} ${height}`,
      width,
      height,
      role: "img",
      "aria-labelledby": `${uid}-title ${uid}-desc`,
      preserveAspectRatio: "xMidYMid meet",
    });
    const title = svgElement("title", { id: `${uid}-title` });
    title.textContent = titleText;
    const description = svgElement("desc", { id: `${uid}-desc` });
    description.textContent = descriptionText;
    svg.append(title, description);
    container.appendChild(svg);
    return { svg, uid, width, height };
  }

  function addA11yList(container, entries, label) {
    if (!entries.length) return;
    const list = element("ul", "sr-only chart-a11y");
    list.setAttribute("aria-label", label);
    for (const entry of entries) {
      list.appendChild(element("li", "", entry));
    }
    container.appendChild(list);
  }

  function ensureTooltip(container) {
    let tooltip = container.querySelector(":scope > .chart-tooltip");
    if (!tooltip) {
      tooltip = element("div", "chart-tooltip");
      tooltip.hidden = true;
      tooltip.setAttribute("aria-hidden", "true");
      container.appendChild(tooltip);
    }
    return tooltip;
  }

  function fillTooltip(tooltip, content) {
    tooltip.replaceChildren();
    tooltip.appendChild(element("span", "chart-tooltip__title", content.title));
    for (const [label, value] of content.rows) {
      if (value === undefined || value === null) continue;
      const row = element("span", "chart-tooltip__row");
      row.appendChild(element("span", "", label));
      row.appendChild(element("strong", "", value));
      tooltip.appendChild(row);
    }
  }

  function positionTooltip(container, tooltip, target) {
    const containerRect = container.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    let left = targetRect.left - containerRect.left + targetRect.width / 2 - tooltipRect.width / 2;
    let top = targetRect.top - containerRect.top - tooltipRect.height - 10;
    if (top < 4) top = targetRect.bottom - containerRect.top + 10;
    left = clamp(left, 5, Math.max(5, containerRect.width - tooltipRect.width - 5));
    top = clamp(top, 4, Math.max(4, containerRect.height - tooltipRect.height - 4));
    tooltip.style.transform = "none";
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  }

  function bindTooltip(container, target, contentFactory) {
    const tooltip = ensureTooltip(container);
    const show = () => {
      const content = contentFactory();
      if (!content) return;
      fillTooltip(tooltip, content);
      tooltip.hidden = false;
      positionTooltip(container, tooltip, target);
    };
    const hide = () => {
      tooltip.hidden = true;
    };
    target.addEventListener("mouseenter", show);
    target.addEventListener("focus", show);
    target.addEventListener("mouseleave", hide);
    target.addEventListener("blur", hide);
  }

  function addLegendGradient(defs, id, stops, vertical = false) {
    const gradient = svgElement("linearGradient", {
      id,
      x1: "0",
      y1: "0",
      x2: vertical ? "0" : "1",
      y2: vertical ? "1" : "0",
    });
    for (const [offset, color, opacity] of stops) {
      gradient.appendChild(
        svgElement("stop", {
          offset,
          "stop-color": color,
          "stop-opacity": opacity,
        }),
      );
    }
    defs.appendChild(gradient);
    return gradient;
  }

  /* ------------------------------------------------------------------------
     Summary
     ------------------------------------------------------------------------ */

  function resetSummary() {
    setText("stat-agents", "—");
    setText("stat-agents-sub", "awaiting results");
    setText("stat-matches", "—");
    setText("stat-matches-sub", "side-swapped");
    setText("stat-elo", "—");
    setText("stat-elo-sub", "no standings loaded");
    setText("stat-speed", "—");
    setText("stat-speed-sub", "decisions / second");
  }

  function renderSummary() {
    const { rows, matches, hasMatches, status } = state.leaderboard;
    if (status !== "ready") {
      resetSummary();
      return;
    }

    setText("stat-agents", String(rows.length));
    setText(
      "stat-agents-sub",
      rows.length === 0 ? "no contenders reported" : rows.length === 1 ? "contender in report" : "contenders in report",
    );

    setText("stat-matches", hasMatches ? formatInteger(matches.length) : "—");
    setText(
      "stat-matches-sub",
      hasMatches
        ? matches.length === 1
          ? "side-swapped matchup"
          : "side-swapped matchups"
        : "match metadata missing",
    );

    const top = rows.find((row) => row.rating !== null);
    setText("stat-elo", top ? formatElo(top.rating) : "—");
    const eloSub = setText("stat-elo-sub", top ? top.agent : "no rating reported");
    if (eloSub) {
      if (top) eloSub.title = top.agent;
      else eloSub.removeAttribute("title");
    }

    const speedRows = rows.filter((row) => row.dps !== null).sort((a, b) => b.dps - a.dps);
    const fastest = speedRows[0];
    setText("stat-speed", fastest ? formatDecisionsPerSecond(fastest.dps) : "—");
    const speedSub = setText(
      "stat-speed-sub",
      fastest ? `${fastest.agent} · decisions/s` : "decisions/second not reported",
    );
    if (speedSub) {
      if (fastest) speedSub.title = `${fastest.agent}: ${formatDecisionsPerSecond(fastest.dps)} decisions/second`;
      else speedSub.removeAttribute("title");
    }
  }

  /* ------------------------------------------------------------------------
     Leaderboard
     ------------------------------------------------------------------------ */

  function renderLeaderboard() {
    renderSummary();
    const { rows, matches, hasMatches } = state.leaderboard;
    const matchText = hasMatches ? pluralCount(matches.length, "matchup") : "matches unavailable";
    setDatasetTag(
      "leaderboard-meta",
      rows.length ? `${pluralCount(rows.length, "agent")} · ${matchText}` : "No standings",
      rows.length ? "live" : "unavailable",
    );
    renderEloChart(rows);
    renderLeaderboardTable(rows);
    renderPareto();
  }

  function renderLeaderboardFailure() {
    resetSummary();
    setDatasetTag("leaderboard-meta", "Dataset unavailable", "unavailable");
    setDatasetTag("pareto-meta", "Dataset unavailable", "unavailable");

    renderEmptyState(document.getElementById("elo-chart"), {
      title: "Standings unavailable",
      message: "The leaderboard JSON could not be loaded in this deployment.",
      hint: dataHint("leaderboard"),
    });
    renderEmptyState(document.getElementById("leaderboard-table"), {
      title: "No standings to show",
      message: "Generate the benchmark report, then refresh this page.",
      hint: dataHint("leaderboard"),
    });
    renderPareto();
  }

  function renderLeaderboardTable(rows) {
    const host = document.getElementById("leaderboard-table");
    if (!host) return;

    if (!rows.length) {
      renderEmptyState(host, {
        title: "No standings yet",
        message: "The leaderboard report is present but contains no ranked agents.",
        showCommand: false,
        hint: "Expected a non-empty standings array.",
      });
      setText("standings-count", "0");
      return;
    }

    setText("standings-count", String(rows.length));

    const table = element("table", "data-table");
    const caption = element(
      "caption",
      "sr-only",
      "Standings with Elo rating, win rate, 95 percent confidence interval, and decisions per second.",
    );
    table.appendChild(caption);

    const thead = element("thead");
    const headRow = element("tr");
    for (const [label, className] of [
      ["Agent", ""],
      ["Elo", "num"],
      ["Win rate", "num"],
      ["95% CI", "num"],
      ["Decisions/s", "num"],
    ]) {
      const th = element("th", className, label);
      th.scope = "col";
      headRow.appendChild(th);
    }
    thead.appendChild(headRow);

    const tbody = element("tbody");
    for (const row of rows) {
      const tr = element("tr");

      const agentCell = element("td", "agent-cell");
      agentCell.dataset.label = "Agent";
      const agentLine = element("div", "agent-line");
      const rank = element("span", "rank-index", String(row.rank).padStart(2, "0"));
      if (row.rank <= 3) rank.dataset.podium = String(row.rank);
      const agentName = element("span", "agent-name", row.agent);
      agentName.title = row.agent;
      agentLine.append(rank, agentName);
      agentCell.appendChild(agentLine);
      const record = row.hasRecord
        ? `${formatInteger(row.wins)}W · ${formatInteger(row.losses)}L · ${formatInteger(row.draws)}D`
        : "record not reported";
      agentCell.appendChild(element("div", "agent-sub", record));
      tr.appendChild(agentCell);

      const eloCell = element("td", "num");
      eloCell.dataset.label = "Elo";
      eloCell.appendChild(
        element("span", row.rating !== null ? "elo-value" : "muted-value", formatElo(row.rating)),
      );
      tr.appendChild(eloCell);

      const rateCell = element("td", "num");
      rateCell.dataset.label = "Win rate";
      if (row.winRate !== null) {
        rateCell.appendChild(element("span", "rate-badge", formatPercent(row.winRate)));
      } else {
        rateCell.appendChild(element("span", "muted-value", "—"));
      }
      tr.appendChild(rateCell);

      const ciCell = element("td", "num");
      ciCell.dataset.label = "95% CI";
      ciCell.appendChild(
        element("span", row.interval ? "ci-value" : "muted-value", formatInterval(row.interval)),
      );
      tr.appendChild(ciCell);

      const dpsCell = element("td", "num");
      dpsCell.dataset.label = "Decisions/s";
      dpsCell.appendChild(
        element(
          "span",
          row.dps !== null ? "dps-value" : "muted-value",
          row.dps !== null ? formatDecisionsPerSecond(row.dps) : "—",
        ),
      );
      tr.appendChild(dpsCell);

      tbody.appendChild(tr);
    }

    table.append(thead, tbody);
    host.replaceChildren(table);
  }

  function renderEloChart(rows) {
    const container = document.getElementById("elo-chart");
    if (!container) return;
    const plotted = rows.filter((row) => row.rating !== null);

    if (!plotted.length) {
      renderEmptyState(container, {
        title: rows.length ? "No ratings reported" : "No standings yet",
        message: rows.length
          ? "The standings are present, but no Elo rating was found."
          : "The leaderboard report is present but contains no ranked agents.",
        showCommand: !rows.length,
        hint: rows.length ? "Expected a numeric rating on each standing." : "Expected a non-empty standings array.",
      });
      return;
    }

    const width = chartWidth(container);
    const compact = width < 380;
    const rowHeight = compact ? 36 : 40;
    const height = 24 + plotted.length * rowHeight + 52;
    const left = compact ? 84 : Math.min(130, Math.max(104, width * 0.22));
    const right = 56;
    const top = 12;
    const bottom = height - 44;
    const plotWidth = Math.max(30, width - left - right);
    const ratings = plotted.map((row) => row.rating);
    const minimum = Math.min(...ratings);
    const maximum = Math.max(...ratings);
    const padding = Math.max(14, (maximum - minimum) * 0.4);
    const scale = niceScale(minimum - padding, maximum + padding, 4);

    const { svg, uid } = createChart(
      container,
      width,
      height,
      "Elo rating by agent",
      "Horizontal bar chart of Bradley-Terry Elo ratings. The accompanying table contains exact values, win rates, confidence intervals, and throughput.",
    );

    const defs = svgElement("defs");
    addLegendGradient(defs, `${uid}-bars`, [
      ["0%", "#c9a96a", "0.94"],
      ["58%", "#b8a17a", "0.9"],
      ["100%", "#7f9cc4", "0.92"],
    ]);
    svg.appendChild(defs);

    for (const tick of scale.ticks) {
      const x =
        left + ((tick - scale.min) / (scale.max - scale.min || 1)) * plotWidth;
      svg.appendChild(
        svgElement("line", {
          x1: x,
          y1: top,
          x2: x,
          y2: bottom,
          class: "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x,
          y: bottom + 17,
          class: "tick-label",
          "text-anchor": "middle",
        },
        formatInteger(tick),
      );
    }

    plotted.forEach((row, index) => {
      const centerY = top + index * rowHeight + rowHeight / 2;
      const rowGroup = svgElement("g", { class: "bar-row" });
      const barWidth = clamp(
        ((row.rating - scale.min) / (scale.max - scale.min || 1)) * plotWidth,
        2,
        plotWidth,
      );

      svgText(
        rowGroup,
        {
          x: left - 11,
          y: centerY + 3.5,
          class: "category-label",
          "text-anchor": "end",
        },
        truncateText(row.agent, compact ? 11 : width < 680 ? 14 : 18),
      );

      rowGroup.appendChild(
        svgElement("rect", {
          x: left,
          y: centerY - 5,
          width: plotWidth,
          height: 10,
          rx: 5,
          class: "bar-track",
        }),
      );

      const bar = svgElement("rect", {
        x: left,
        y: centerY - 5,
        width: barWidth,
        height: 10,
        rx: 5,
        fill: `url(#${uid}-bars)`,
        class: "bar-fill",
      });
      bar.style.animationDelay = `${Math.min(index * 55, 360)}ms`;
      const rowTitle = svgElement("title");
      rowTitle.textContent = `${row.agent}: ${formatElo(row.rating)} Elo${
        row.winRate !== null ? `, ${formatPercent(row.winRate)} win rate` : ""
      }`;
      bar.appendChild(rowTitle);
      rowGroup.appendChild(bar);

      svgText(
        rowGroup,
        {
          x: left + barWidth + 8,
          y: centerY + 3.5,
          class: "value-label",
          "text-anchor": "start",
        },
        formatElo(row.rating),
      );

      svg.appendChild(rowGroup);
    });

    svgText(
      svg,
      {
        x: left + plotWidth / 2,
        y: height - 8,
        class: "axis-title",
        "text-anchor": "middle",
      },
      "Bradley–Terry Elo rating",
    );

    addA11yList(
      container,
      plotted.map(
        (row) =>
          `${row.agent}: ${formatElo(row.rating)} Elo${row.winRate !== null ? `, ${formatPercent(row.winRate)} win rate` : ""}.`,
      ),
      "Elo ratings by agent",
    );
  }

  /* ------------------------------------------------------------------------
     Pareto chart
     ------------------------------------------------------------------------ */

  function computeParetoFrontier(points) {
    return points.filter(
      (point) =>
        !points.some(
          (other) =>
            other !== point &&
            other.dps >= point.dps &&
            other.rating >= point.rating &&
            (other.dps > point.dps || other.rating > point.rating),
        ),
    );
  }

  function overlap(a, b) {
    return !(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y);
  }

  function pointShape(shapeIndex, color) {
    const common = {
      class: "chart-point",
      fill: color,
      stroke: "#0e0f12",
      "stroke-width": "1.5",
    };
    switch (shapeIndex % 4) {
      case 1:
        return svgElement("rect", { ...common, x: -4.6, y: -4.6, width: 9.2, height: 9.2, rx: 1.6 });
      case 2:
        return svgElement("path", { ...common, d: "M0 -6 L5.4 0 L0 6 L-5.4 0 Z" });
      case 3:
        return svgElement("path", { ...common, d: "M0 -6.2 L6 4.4 L-6 4.4 Z" });
      default:
        return svgElement("circle", { ...common, cx: 0, cy: 0, r: 5 });
    }
  }

  function updateParetoInsight(points, frontier) {
    const count = document.getElementById("pareto-count");
    const subtitle = document.getElementById("pareto-count-sub");
    const detail = document.getElementById("pareto-detail");
    if (!count || !subtitle || !detail) return;

    if (!points.length) {
      count.textContent = "—";
      subtitle.textContent = "awaiting throughput data";
      detail.textContent = "Awaiting decisions_per_sec metadata.";
      return;
    }

    count.textContent = `${frontier.length} / ${points.length}`;
    subtitle.textContent =
      frontier.length === 1 ? "agent is Pareto-optimal" : "agents are Pareto-optimal";
    const fastest = [...frontier].sort((a, b) => b.dps - a.dps)[0];
    detail.textContent = fastest
      ? `Fastest frontier agent: ${fastest.agent} at ${formatDecisionsPerSecond(fastest.dps)} decisions/s.`
      : "No throughput values were available.";
  }

  function renderPareto() {
    const container = document.getElementById("pareto-chart");
    if (!container) return;
    const dataset = state.leaderboard;

    if (dataset.status !== "ready") {
      renderEmptyState(container, {
        title: "Efficiency view unavailable",
        message: "Leaderboard data is required for the strength-versus-compute chart.",
        hint: dataHint("leaderboard"),
      });
      updateParetoInsight([], []);
      setDatasetTag("pareto-meta", "Dataset unavailable", "unavailable");
      return;
    }

    const points = dataset.rows.filter((row) => row.rating !== null && row.dps !== null);
    if (!points.length) {
      const hasRows = dataset.rows.length > 0;
      const hasRatings = dataset.rows.some((row) => row.rating !== null);
      renderEmptyState(container, {
        title: hasRows && hasRatings ? "No throughput data" : "No efficiency points",
        message:
          hasRows && hasRatings
            ? "Decisions per second is required for this chart. Add decisions_per_sec to standings or match records."
            : "The report needs both a rating and decisions-per-second value for every plotted point.",
        showCommand: false,
        hint:
          hasRows && hasRatings
            ? "Accepted keys: standings[].decisions_per_sec or matches[].decisions_per_sec."
            : "Expected standings with rating and throughput metadata.",
      });
      updateParetoInsight([], []);
      setDatasetTag(
        "pareto-meta",
        hasRows ? "No throughput data" : "No standings",
        "unavailable",
      );
      return;
    }

    setDatasetTag(
      "pareto-meta",
      `${pluralCount(points.length, "agent")} · ${pluralCount(dataset.matches.length, "matchup")}`,
      "live",
    );

    const width = chartWidth(container, 300);
    const compact = width < 500;
    const height = compact ? 300 : 340;
    const left = compact ? 50 : 60;
    const right = compact ? 18 : 26;
    const top = compact ? 26 : 22;
    const bottom = height - 54;
    const plotWidth = width - left - right;
    const plotHeight = bottom - top;

    const xScale = buildXScale(
      points.map((point) => point.dps),
      compact ? 4 : 5,
    );
    const ratings = points.map((point) => point.rating);
    const minimumRating = Math.min(...ratings);
    const maximumRating = Math.max(...ratings);
    const ratingPadding = Math.max(14, (maximumRating - minimumRating) * 0.35);
    const yScale = niceScale(
      minimumRating - ratingPadding,
      maximumRating + ratingPadding,
      compact ? 3 : 4,
    );

    const { svg, uid } = createChart(
      container,
      width,
      height,
      "Strength versus compute Pareto chart",
      "Scatter plot of Elo rating against decisions per second. The dashed line connects agents that are not dominated on both axes. Point shapes and the accompanying text list identify each agent.",
    );

    for (const rating of yScale.ticks) {
      const y = projectY(rating, yScale.min, yScale.max, top, plotHeight);
      svg.appendChild(
        svgElement("line", {
          x1: left,
          y1: y,
          x2: left + plotWidth,
          y2: y,
          class: "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x: left - 9,
          y: y + 3.3,
          class: "tick-label",
          "text-anchor": "end",
        },
        formatInteger(rating),
      );
    }

    for (const tick of xScale.ticks) {
      const x = projectX(tick, xScale, left, plotWidth);
      svg.appendChild(
        svgElement("line", {
          x1: x,
          y1: top,
          x2: x,
          y2: bottom,
          class: "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x,
          y: bottom + 16,
          class: "tick-label",
          "text-anchor": "middle",
        },
        formatCompact(tick),
      );
    }

    svg.appendChild(
      svgElement("line", {
        x1: left,
        y1: bottom,
        x2: left + plotWidth,
        y2: bottom,
        class: "zero-line",
      }),
    );

    const frontier = computeParetoFrontier(points).sort((a, b) => a.dps - b.dps);
    if (frontier.length >= 2) {
      const pathParts = frontier.map((point, index) => {
        const x = projectX(point.dps, xScale, left, plotWidth);
        const y = projectY(point.rating, yScale.min, yScale.max, top, plotHeight);
        return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
      });
      svg.appendChild(
        svgElement("path", {
          d: pathParts.join(" "),
          class: "frontier-line",
        }),
      );
    }

    const plotted = points.map((point, index) => ({
      ...point,
      px: projectX(point.dps, xScale, left, plotWidth),
      py: projectY(point.rating, yScale.min, yScale.max, top, plotHeight),
      color: PALETTE[index % PALETTE.length],
      shapeIndex: index,
    }));

    for (const point of plotted) {
      const group = svgElement("g", {
        class: "point-group",
        transform: `translate(${point.px} ${point.py})`,
        tabindex: "0",
        role: "img",
        "aria-label": `${point.agent}: ${formatElo(point.rating)} Elo at ${formatDecisionsPerSecond(point.dps)} decisions per second.`,
      });
      const title = svgElement("title");
      title.textContent = `${point.agent}: ${formatElo(point.rating)} Elo · ${formatDecisionsPerSecond(point.dps)} decisions/s`;
      group.appendChild(title);
      group.appendChild(pointShape(point.shapeIndex, point.color));
      bindTooltip(container, group, () => ({
        title: point.agent,
        rows: [
          ["Elo", formatElo(point.rating)],
          ["Decisions/s", formatDecisionsPerSecond(point.dps)],
          ["Win rate", point.winRate !== null ? formatPercent(point.winRate) : "—"],
        ],
      }));
      svg.appendChild(group);
    }

    const labelBoxes = [];
    const labelCandidates = [
      { dx: 9, dy: -8, anchor: "start" },
      { dx: -9, dy: -8, anchor: "end" },
      { dx: 9, dy: 16, anchor: "start" },
      { dx: -9, dy: 16, anchor: "end" },
    ];
    const maxLabelLength = compact ? 10 : width < 700 ? 14 : 18;
    for (const point of [...plotted].sort((a, b) => b.rating - a.rating)) {
      const label = truncateText(point.agent, maxLabelLength);
      const boxWidth = label.length * 5.2 + 5;
      const boxHeight = 11;
      let placement = null;

      for (const candidate of labelCandidates) {
        const startX =
          candidate.anchor === "end" ? point.px + candidate.dx - boxWidth : point.px + candidate.dx;
        const box = {
          x: startX,
          y: point.py + candidate.dy - 9,
          w: boxWidth,
          h: boxHeight,
        };
        if (box.x < left + 2 || box.x + box.w > width - right - 2) continue;
        if (box.y < top + 2 || box.y + box.h > bottom - 1) continue;
        if (labelBoxes.some((other) => overlap(box, other))) continue;
        placement = { ...candidate, box };
        break;
      }

      if (!placement) continue;
      labelBoxes.push(placement.box);
      svgText(
        svg,
        {
          x: point.px + placement.dx,
          y: point.py + placement.dy,
          class: "point-label",
          "text-anchor": placement.anchor,
        },
        label,
      );
    }

    svgText(
      svg,
      {
        x: left + plotWidth / 2,
        y: height - 10,
        class: "axis-title",
        "text-anchor": "middle",
      },
      xScale.log ? "Decisions per second (log scale)" : "Decisions per second",
    );
    svgText(
      svg,
      {
        x: 11,
        y: top + plotHeight / 2,
        transform: `rotate(-90 11 ${top + plotHeight / 2})`,
        class: "axis-title",
        "text-anchor": "middle",
      },
      "Elo rating",
    );

    addA11yList(
      container,
      plotted.map(
        (point) =>
          `${point.agent}: ${formatElo(point.rating)} Elo, ${formatDecisionsPerSecond(point.dps)} decisions per second.`,
      ),
      "Strength versus compute data",
    );

    updateParetoInsight(points, frontier);
  }

  /* ------------------------------------------------------------------------
     Learning curves
     ------------------------------------------------------------------------ */

  function renderLearning() {
    const { bc, rl } = state.learning;
    const total = bc.length + rl.length;
    setDatasetTag(
      "learning-meta",
      total ? `${formatInteger(bc.length)} BC / ${formatInteger(rl.length)} RL` : "No checkpoints",
      total ? "live" : "unavailable",
    );

    for (const config of LEARNING_CHARTS) {
      const series = config.key === "bc" ? bc : rl;
      renderLearningChart(document.getElementById(config.containerId), series, config);
    }
  }

  function renderLearningFailure() {
    setDatasetTag("learning-meta", "Dataset unavailable", "unavailable");
    for (const config of LEARNING_CHARTS) {
      renderEmptyState(document.getElementById(config.containerId), {
        title: "Learning data unavailable",
        message: "The learning-curve JSON could not be loaded.",
        hint: dataHint("learning"),
      });
      setMetric(config.metricId, "—");
    }
  }

  function renderLearningChart(container, series, options) {
    if (!container) return;

    if (!series.length) {
      renderEmptyState(container, {
        title: options.emptyTitle,
        message: options.emptyMessage,
        showCommand: false,
        hint: options.emptyHint,
      });
      setMetric(options.metricId, "—");
      return;
    }

    const finalPoint = series[series.length - 1];
    const peakPoint = series.reduce((best, point) => (point.y > best.y ? point : best), series[0]);
    setMetric(
      options.metricId,
      formatPercent(finalPoint.y),
      `Final: ${formatPercent(finalPoint.y)}. Peak: ${formatPercent(peakPoint.y)} at ${formatCompact(peakPoint.x)} ${options.xAxisLabel.toLowerCase()}.`,
    );

    const width = chartWidth(container);
    const compact = width < 500;
    const height = compact ? 245 : 282;
    const left = compact ? 44 : 48;
    const right = compact ? 14 : 18;
    const top = 20;
    const bottom = height - 50;
    const plotWidth = width - left - right;
    const plotHeight = bottom - top;
    const xScale = buildXScale(
      series.map((point) => point.x),
      compact ? 4 : 5,
    );
    const xAxisTitle = `${options.xAxisLabel}${xScale.log ? " (log scale)" : ""}`;

    const { svg, uid } = createChart(
      container,
      width,
      height,
      options.chartTitle,
      options.chartDescription,
    );

    const defs = svgElement("defs");
    addLegendGradient(
      defs,
      `${uid}-area`,
      [
        ["0%", options.color, "0.26"],
        ["100%", options.color, "0.015"],
      ],
      true,
    );
    svg.appendChild(defs);

    const yTicks = [0, 0.25, 0.5, 0.75, 1];
    for (const tick of yTicks) {
      const y = projectY(tick, 0, 1, top, plotHeight);
      svg.appendChild(
        svgElement("line", {
          x1: left,
          y1: y,
          x2: left + plotWidth,
          y2: y,
          class: tick === 0 ? "zero-line" : "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x: left - 8,
          y: y + 3.4,
          class: "tick-label",
          "text-anchor": "end",
        },
        `${Math.round(tick * 100)}%`,
      );
    }

    for (const tick of xScale.ticks) {
      const x = projectX(tick, xScale, left, plotWidth);
      svg.appendChild(
        svgElement("line", {
          x1: x,
          y1: top,
          x2: x,
          y2: bottom,
          class: "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x,
          y: bottom + 16,
          class: "tick-label",
          "text-anchor": "middle",
        },
        formatCompact(tick),
      );
    }

    const chanceY = projectY(0.5, 0, 1, top, plotHeight);
    svg.appendChild(
      svgElement("line", {
        x1: left,
        y1: chanceY,
        x2: left + plotWidth,
        y2: chanceY,
        class: "chance-line",
      }),
    );
    svgText(
      svg,
      {
        x: left + plotWidth - 1,
        y: chanceY - 5,
        class: "chance-label",
        "text-anchor": "end",
      },
      "chance",
    );

    const coordinates = series.map((point) => ({
      ...point,
      px: projectX(point.x, xScale, left, plotWidth),
      py: projectY(point.y, 0, 1, top, plotHeight),
    }));

    if (coordinates.length >= 2) {
      const linePath = coordinates
        .map((point, index) => `${index === 0 ? "M" : "L"}${point.px.toFixed(2)},${point.py.toFixed(2)}`)
        .join(" ");
      const areaPath = `${linePath} L${coordinates[coordinates.length - 1].px.toFixed(2)},${bottom} L${coordinates[0].px.toFixed(2)},${bottom} Z`;
      svg.appendChild(
        svgElement("path", {
          d: areaPath,
          fill: `url(#${uid}-area)`,
          class: "area-fill",
        }),
      );
      const line = svgElement("path", {
        d: linePath,
        class: "line-path",
        stroke: options.color,
        pathLength: "1",
      });
      svg.appendChild(line);
    }

    coordinates.forEach((point, index) => {
      const group = svgElement("g", {
        class: "point-group",
        transform: `translate(${point.px} ${point.py})`,
        tabindex: "0",
        role: "img",
        "aria-label": `${formatCompact(point.x)} ${options.xAxisLabel.toLowerCase()}: ${formatPercent(point.y)} win rate.`,
      });
      const title = svgElement("title");
      title.textContent = `${formatCompact(point.x)} ${options.xAxisLabel.toLowerCase()} · ${formatPercent(point.y)} win rate`;
      group.appendChild(title);

      if (index === coordinates.length - 1) {
        group.appendChild(
          svgElement("circle", {
            r: 7,
            fill: options.color,
            opacity: "0.14",
          }),
        );
      }

      group.appendChild(
        svgElement("circle", {
          class: "chart-point",
          cx: 0,
          cy: 0,
          r: index === coordinates.length - 1 ? 4.4 : 3.4,
          fill: "#14161a",
          stroke: options.color,
          "stroke-width": index === coordinates.length - 1 ? 2 : 1.6,
        }),
      );

      bindTooltip(container, group, () => ({
        title: options.seriesName,
        rows: [
          [options.xAxisLabel, formatCompact(point.x)],
          ["Win rate", formatPercent(point.y)],
        ],
      }));
      svg.appendChild(group);
    });

    svgText(
      svg,
      {
        x: left + plotWidth / 2,
        y: height - 8,
        class: "axis-title",
        "text-anchor": "middle",
      },
      xAxisTitle,
    );
    svgText(
      svg,
      {
        x: 11,
        y: top + plotHeight / 2,
        transform: `rotate(-90 11 ${top + plotHeight / 2})`,
        class: "axis-title",
        "text-anchor": "middle",
      },
      "Win rate",
    );

    addA11yList(
      container,
      coordinates.map(
        (point) =>
          `${formatCompact(point.x)} ${options.xAxisLabel.toLowerCase()}: ${formatPercent(point.y)} win rate.`,
      ),
      `${options.seriesName} data points`,
    );
  }

  /* ------------------------------------------------------------------------
     Generalization
     ------------------------------------------------------------------------ */

  function renderGeneralization() {
    const { rows, rawCount } = state.generalization;
    const gaps = rows.map((row) => row.gap).filter((gap) => gap !== null);
    const meanGap = gaps.length ? gaps.reduce((sum, gap) => sum + gap, 0) / gaps.length : null;
    const gapLabel = gaps.length ? `mean Δ ${formatPercentPoints(meanGap)}` : "no matched pairs";

    setDatasetTag(
      "generalization-meta",
      rows.length ? `${pluralCount(rows.length, "agent")} · ${gapLabel}` : "No results",
      rows.length ? "live" : "unavailable",
    );
    setText("generalization-count", rows.length ? String(rows.length) : "0");

    renderGeneralizationChart(rows, rawCount);
    renderGeneralizationTable(rows, rawCount);
  }

  function renderGeneralizationFailure() {
    setDatasetTag("generalization-meta", "Dataset unavailable", "unavailable");
    setText("generalization-count", "—");
    renderEmptyState(document.getElementById("generalization-chart"), {
      title: "Transfer data unavailable",
      message: "The generalization JSON could not be loaded.",
      hint: dataHint("generalization"),
    });
    renderEmptyState(document.getElementById("generalization-table"), {
      title: "No transfer readout",
      message: "Generate the benchmark report, then refresh this page.",
      hint: dataHint("generalization"),
    });
  }

  function renderGeneralizationChart(rows, rawCount) {
    const container = document.getElementById("generalization-chart");
    if (!container) return;

    if (!rows.length) {
      renderEmptyState(container, {
        title: rawCount ? "No win rates reported" : "No held-out results",
        message: rawCount
          ? "Results are present, but no train or held-out win rates were found."
          : "The report contains no generalization results.",
        showCommand: false,
        hint: rawCount
          ? "Expected train_win_rate and heldout_win_rate on each result."
          : "Expected a results array with agent win rates.",
      });
      return;
    }

    const width = chartWidth(container, 300);
    const compact = width < 500;
    const rowHeight = compact ? 52 : 56;
    const height = 20 + rows.length * rowHeight + 58;
    const left = compact ? 76 : Math.min(116, Math.max(92, width * 0.2));
    const right = 52;
    const top = 16;
    const bottom = height - 46;
    const plotWidth = Math.max(30, width - left - right);
    const barHeight = 11;

    const { svg, uid } = createChart(
      container,
      width,
      height,
      "Train and held-out win rate by agent",
      "Grouped horizontal bar chart comparing training win rate with held-out species win rate for each agent.",
    );

    const defs = svgElement("defs");
    addLegendGradient(defs, `${uid}-train`, [
      ["0%", "#c9a96a", "0.9"],
      ["100%", "#e0c58f", "0.95"],
    ]);
    addLegendGradient(defs, `${uid}-held`, [
      ["0%", "#7f9cc4", "0.92"],
      ["100%", "#b8c6d8", "0.95"],
    ]);
    svg.appendChild(defs);

    for (const tick of [0, 0.25, 0.5, 0.75, 1]) {
      const x = left + tick * plotWidth;
      svg.appendChild(
        svgElement("line", {
          x1: x,
          y1: top,
          x2: x,
          y2: bottom,
          class: tick === 0 ? "zero-line" : "grid-line",
        }),
      );
      svgText(
        svg,
        {
          x,
          y: bottom + 16,
          class: "tick-label",
          "text-anchor": "middle",
        },
        `${Math.round(tick * 100)}%`,
      );
    }

    rows.forEach((row, index) => {
      const centerY = top + index * rowHeight + rowHeight / 2;
      const trainY = centerY - barHeight - 2;
      const heldY = centerY + 2;

      svgText(
        svg,
        {
          x: left - 10,
          y: centerY + 3.5,
          class: "category-label",
          "text-anchor": "end",
        },
        truncateText(row.agent, compact ? 10 : 14),
      );

      for (const [value, y, gradient, name] of [
        [row.train, trainY, `${uid}-train`, "train"],
        [row.heldOut, heldY, `${uid}-held`, "held-out"],
      ]) {
        svg.appendChild(
          svgElement("rect", {
            x: left,
            y,
            width: plotWidth,
            height: barHeight,
            rx: 5.5,
            class: "bar-track",
          }),
        );

        if (value !== null) {
          const barWidth = value > 0 ? Math.max(2, value * plotWidth) : 0;
          const bar = svgElement("rect", {
            x: left,
            y,
            width: barWidth,
            height: barHeight,
            rx: 5.5,
            fill: `url(#${gradient})`,
            class: "bar-fill",
          });
          const barTitle = svgElement("title");
          barTitle.textContent = `${row.agent} — ${name}: ${formatPercent(value)}`;
          bar.appendChild(barTitle);
          svg.appendChild(bar);
          svgText(
            svg,
            {
              x: left + barWidth + 6,
              y: y + 8.8,
              class: "value-label",
              "text-anchor": "start",
            },
            formatPercent(value),
          );
        } else {
          svgText(
            svg,
            {
              x: left + 7,
              y: y + 8.8,
              class: "value-label",
              "text-anchor": "start",
            },
            "—",
          );
        }
      }
    });

    svgText(
      svg,
      {
        x: left + plotWidth / 2,
        y: height - 9,
        class: "axis-title",
        "text-anchor": "middle",
      },
      "Win rate",
    );

    addA11yList(
      container,
      rows.map((row) => {
        const train = row.train !== null ? `${formatPercent(row.train)} train` : "train not reported";
        const heldOut =
          row.heldOut !== null ? `${formatPercent(row.heldOut)} held-out` : "held-out not reported";
        return `${row.agent}: ${train}, ${heldOut}.`;
      }),
      "Train and held-out win rates",
    );
  }

  function renderGeneralizationTable(rows, rawCount) {
    const host = document.getElementById("generalization-table");
    if (!host) return;

    if (!rows.length) {
      renderEmptyState(host, {
        title: rawCount ? "No rates reported" : "No transfer results",
        message: rawCount
          ? "The results array is present, but no win-rate values could be read."
          : "The generalization report contains no agent results.",
        showCommand: false,
        hint: "Expected agent, train_win_rate, and heldout_win_rate.",
      });
      return;
    }

    const table = element("table", "data-table");
    const caption = element(
      "caption",
      "sr-only",
      "Train and held-out species win rates by agent, including the transfer gap.",
    );
    table.appendChild(caption);

    const thead = element("thead");
    const headRow = element("tr");
    for (const [label, className] of [
      ["Agent", ""],
      ["Train", "num"],
      ["Held-out", "num"],
      ["Δ", "num"],
    ]) {
      const th = element("th", className, label);
      th.scope = "col";
      if (label === "Δ") th.title = "Held-out win rate minus training win rate.";
      headRow.appendChild(th);
    }
    thead.appendChild(headRow);

    const tbody = element("tbody");
    rows.forEach((row, index) => {
      const tr = element("tr");

      const agentCell = element("td", "agent-cell");
      agentCell.dataset.label = "Agent";
      const line = element("div", "agent-line");
      line.appendChild(element("span", "rank-index", String(index + 1).padStart(2, "0")));
      const name = element("span", "agent-name", row.agent);
      name.title = row.agent;
      line.appendChild(name);
      agentCell.appendChild(line);
      tr.appendChild(agentCell);

      const trainCell = element("td", "num");
      trainCell.dataset.label = "Train";
      trainCell.appendChild(
        element(
          "span",
          row.train !== null ? "ci-value" : "muted-value",
          row.train !== null ? formatPercent(row.train) : "—",
        ),
      );
      tr.appendChild(trainCell);

      const heldCell = element("td", "num");
      heldCell.dataset.label = "Held-out";
      heldCell.appendChild(
        element(
          "span",
          row.heldOut !== null ? "rate-badge" : "muted-value",
          row.heldOut !== null ? formatPercent(row.heldOut) : "—",
        ),
      );
      tr.appendChild(heldCell);

      const gapCell = element("td", "num");
      gapCell.dataset.label = "Δ";
      let gapClass = "delta-value delta-value--flat";
      if (row.gap !== null) {
        gapClass =
          row.gap < -0.0005
            ? "delta-value delta-value--neg"
            : row.gap > 0.0005
              ? "delta-value delta-value--pos"
              : "delta-value delta-value--flat";
      }
      gapCell.appendChild(
        element("span", gapClass, row.gap !== null ? formatPercentPoints(row.gap) : "—"),
      );
      tr.appendChild(gapCell);

      tbody.appendChild(tr);
    });

    table.append(thead, tbody);
    host.replaceChildren(table);
  }

  /* ------------------------------------------------------------------------
     Copy-to-clipboard and resize
     ------------------------------------------------------------------------ */

  function legacyCopy(text) {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.top = "-1000px";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    let copied = false;
    try {
      copied = document.execCommand("copy");
    } finally {
      area.remove();
    }
    if (!copied) throw new Error("Copy command was rejected");
  }

  function setupCopyButton() {
    const button = document.getElementById("copy-command");
    const status = document.getElementById("copy-status");
    if (!button) return;

    button.addEventListener("click", async () => {
      const text = button.dataset.copy || REPORT_COMMAND;
      const label = button.querySelector("span");
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text);
        } else {
          legacyCopy(text);
        }
        window.clearTimeout(copyResetTimer);
        button.classList.add("is-copied");
        if (label) label.textContent = "Copied";
        if (status) status.textContent = `Copied: ${text}`;
        copyResetTimer = window.setTimeout(() => {
          button.classList.remove("is-copied");
          if (label) label.textContent = "Copy command";
          if (status) status.textContent = "";
        }, 2200);
      } catch (error) {
        console.warn("[PokéLab] Clipboard write failed.", error);
        if (status) status.textContent = `Copy failed. Run manually: ${text}`;
      }
    });
  }

  function redrawCharts() {
    if (state.leaderboard.status === "ready") {
      renderEloChart(state.leaderboard.rows);
      renderPareto();
    }
    if (state.learning.status === "ready") {
      for (const config of LEARNING_CHARTS) {
        const series = config.key === "bc" ? state.learning.bc : state.learning.rl;
        renderLearningChart(document.getElementById(config.containerId), series, config);
      }
    }
    if (state.generalization.status === "ready") {
      renderGeneralizationChart(state.generalization.rows, state.generalization.rawCount);
    }
  }

  /* ------------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------------ */

  function initialize() {
    setupCopyButton();
    window.addEventListener("resize", debounce(redrawCharts, 160));

    const tasks = [loadLeaderboard(), loadLearning(), loadGeneralization()];
    Promise.allSettled(tasks).then(finalizeBanner);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
