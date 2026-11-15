(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const number = new Intl.NumberFormat("fr-CA", { maximumFractionDigits: 1 });
  const whole = new Intl.NumberFormat("fr-CA", { maximumFractionDigits: 0 });
  const dateFmt = new Intl.DateTimeFormat("fr-CA", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
  const state = { bootstrap: null, persona: "robert", result: null, previous: null, chart: "value", busy: false, dirty: false };
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const numeric = (value) => typeof value === "number" && Number.isFinite(value);
  const pct = (value) => numeric(value) ? `${number.format(value)} %` : "—";
  const money = (value) => numeric(value) ? `${whole.format(value)} $` : "—";
  const text = (value) => typeof value === "string" ? value : value?.text || value?.message || "";
  const formatDate = (value) => {
    const date = new Date(String(value).slice(0, 10) + "T12:00:00Z");
    return Number.isNaN(date.getTime()) ? String(value || "—") : dateFmt.format(date);
  };
  const safeUrl = (value) => {
    if (typeof value !== "string" || !value.trim()) return null;
    try {
      const url = new URL(value, location.origin);
      return ["https:", "http:"].includes(url.protocol) ? url.href : null;
    } catch { return null; }
  };

  function showMessage(message) {
    $("#global-message").textContent = message || "";
    $("#global-message").hidden = !message;
  }

  function status(message, kind = "") {
    $("#analysis-status").className = `analysis-status ${kind}`;
    $("#analysis-status").innerHTML = `<span class="status-dot"></span><span>${escape(message)}</span>`;
  }

  function setBusy(busy, ai = false) {
    state.busy = busy;
    $("#analyze-btn").disabled = busy;
    $("#recalculate-btn").disabled = busy;
    $("#reset-btn").disabled = busy;
    $("#undo-btn").disabled = busy || !state.previous;
    $$(".persona-option").forEach((button) => { button.disabled = busy; });
    $$("#view-atelier input,#view-atelier select,#view-atelier textarea,.portfolio-row button,#add-holding").forEach((control) => { control.disabled = busy; });
    $("#result-card").setAttribute("aria-busy", String(busy));
    $("#analyze-btn").innerHTML = busy && ai
      ? '<span class="loader"></span><span>L’agent étudie la demande…</span>'
      : '<span class="sparkle" aria-hidden="true">✳</span><span>Analyser avec l’agent</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11M10 5l5 5-5 5"/></svg>';
    $("#recalculate-btn").innerHTML = busy && !ai
      ? '<span class="loader"></span> Calcul en cours…'
      : '<span aria-hidden="true">↻</span> Recalculer la comparaison';
  }

  function setDirty(value = true) {
    state.dirty = value;
    $("#dirty-note").hidden = !value;
    $("#export-btn").disabled = !state.result;
    if (value && !state.busy) {
      status("Hypothèses modifiées · les résultats correspondent encore à la dernière analyse.");
    }
  }

  function navigate(view, sourceId) {
    if (!["atelier", "preuves", "methode"].includes(view)) return;
    $$(".view").forEach((section) => { section.hidden = section.id !== `view-${view}`; });
    $$(".nav-item").forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    $("#view-label").textContent = { atelier: "L’atelier", preuves: "Dossier de preuves", methode: "La méthode" }[view];
    window.scrollTo({ top: 0, behavior: "instant" });
    if (view === "atelier" && state.result) renderChart();
    if (sourceId) {
      const target = [...$$(".source-item")].find((element) => element.dataset.sourceId === sourceId);
      if (target) {
        target.scrollIntoView({ block: "center", behavior: "smooth" });
        target.classList.remove("highlight");
        void target.offsetWidth;
        target.classList.add("highlight");
      }
    }
  }

  function assetOptions(selected, used = []) {
    return (state.bootstrap?.assets || []).map((asset) => {
      const ticker = asset.ticker;
      return `<option value="${escape(ticker)}" ${ticker === selected ? "selected" : ""} ${used.includes(ticker) && ticker !== selected ? "disabled" : ""}>${escape(ticker)}${asset.name ? " · " + escape(asset.name) : ""}</option>`;
    }).join("");
  }

  function renderPortfolio(portfolio) {
    const used = portfolio.map((holding) => holding.ticker);
    $("#portfolio-rows").innerHTML = portfolio.map((holding) =>
      `<div class="portfolio-row"><select aria-label="Actif du portefeuille">${assetOptions(holding.ticker, used)}</select><input type="number" min="0" max="100" step="0.1" value="${Number((holding.weight * 100).toFixed(4))}" aria-label="Poids de ${escape(holding.ticker)} en pourcentage"><span>%</span><button type="button" aria-label="Retirer ${escape(holding.ticker)}" title="Retirer cet actif">×</button></div>`
    ).join("");
    $$(".portfolio-row select,.portfolio-row input").forEach((input) => input.addEventListener("change", () => {
      updatePortfolioTotal();
      updateBaselineWeight();
      setDirty();
    }));
    $$(".portfolio-row button").forEach((button) => button.addEventListener("click", () => {
      button.closest(".portfolio-row").remove();
      updatePortfolioTotal();
      updateBaselineWeight();
      setDirty();
    }));
    updatePortfolioTotal();
  }

  function readPortfolio() {
    return $$(".portfolio-row").map((row) => ({
      ticker: row.querySelector("select").value,
      weight: Number(row.querySelector("input").value) / 100,
    }));
  }

  function updatePortfolioTotal() {
    const sum = readPortfolio().reduce((total, holding) => total + holding.weight, 0);
    $("#portfolio-total").textContent = pct(sum * 100);
    $("#portfolio-total").classList.toggle("invalid", Math.abs(sum - 1) > 1e-7);
  }

  function updateBaselineWeight() {
    const ticker = $("#focus-ticker").value;
    const holding = readPortfolio().find((item) => item.ticker === ticker);
    $("#baseline-weight").innerHTML = `${number.format((holding?.weight || 0) * 100)}<small>%</small>`;
  }

  function updateSlider(value) {
    const safe = Math.max(0, Math.min(100, Number(value) || 0));
    $("#focus-slider").value = safe;
    $("#focus-weight").value = safe;
    $("#focus-slider").style.background = `linear-gradient(to right,#839e58 0%,#839e58 ${safe}%,#e5eadc ${safe}%,#e5eadc 100%)`;
  }

  function applyPayload(payload) {
    $("#prompt").value = payload.prompt || "";
    $("#horizon").value = payload.settings.horizon_years;
    $("#capital").value = payload.settings.capital;
    $("#comfort").value = payload.settings.max_drawdown_pct;
    $("#focus-ticker").innerHTML = assetOptions(payload.settings.focus_ticker);
    updateSlider(payload.settings.focus_weight);
    renderPortfolio(payload.portfolio);
    updateBaselineWeight();
  }

  function selectPersona(id, calculate = true) {
    const persona = state.bootstrap.personas.find((item) => item.id === id);
    if (!persona) return;
    state.persona = id;
    $$(".persona-option").forEach((button) => {
      const active = button.dataset.persona === id;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    $("#profile-avatar").textContent = persona.name.slice(0, 1);
    $("#profile-name").textContent = persona.name;
    $("#profile-age").textContent = `${persona.age} ans · ${persona.horizon}`;
    $("#profile-description").textContent = persona.description;
    applyPayload(persona);
    setDirty();
    if (calculate) analyze(false);
  }

  function collectPayload(useAi) {
    const portfolio = readPortfolio();
    if (!portfolio.length) throw new Error("Ajoutez au moins un actif au portefeuille de départ.");
    if (portfolio.some((holding) => !numeric(holding.weight) || holding.weight < 0 || holding.weight > 1)) {
      throw new Error("Chaque poids doit être compris entre 0 % et 100 %.");
    }
    const total = portfolio.reduce((sum, holding) => sum + holding.weight, 0);
    if (Math.abs(total - 1) > 1e-7) throw new Error(`Le portefeuille totalise ${pct(total * 100)}. Ajustez les poids pour atteindre 100 %.`);
    if (new Set(portfolio.map((holding) => holding.ticker)).size !== portfolio.length) throw new Error("Un même actif ne peut apparaître qu’une fois dans le portefeuille.");
    const horizon = Number($("#horizon").value);
    const capital = Number($("#capital").value);
    const comfort = Number($("#comfort").value);
    const focus = Number($("#focus-weight").value);
    if (!(horizon > 0 && horizon <= 50)) throw new Error("L’horizon doit être compris entre 1 et 50 ans.");
    if (!(capital >= 1 && capital <= 1e9)) throw new Error("Le capital simulé doit être compris entre 1 et 1 milliard de CAD.");
    if (!(comfort >= 0 && comfort <= 100 && focus >= 0 && focus <= 100)) throw new Error("Les pourcentages doivent être compris entre 0 et 100.");
    return {
      persona: state.persona, prompt: $("#prompt").value.trim(), portfolio, use_ai: useAi,
      settings: { horizon_years: horizon, capital, currency: "CAD", max_drawdown_pct: comfort, focus_ticker: $("#focus-ticker").value, focus_weight: focus },
    };
  }

  async function analyze(useAi) {
    if (state.busy) return;
    let payload;
    try { payload = collectPayload(useAi); }
    catch (error) { showMessage(error.message); return; }
    showMessage("");
    setBusy(true, useAi);
    status(useAi ? "Analyse en cours sur AWS Bedrock · les résultats seront affichés à réception." : "Calcul des deux hypothèses sur le même historique…", "busy");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), useAi ? 240000 : 60000);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload), signal: controller.signal,
      });
      let result;
      try { result = await response.json(); }
      catch { throw new Error("Le serveur n’a pas renvoyé une réponse lisible. Vérifiez qu’AlphaForge est bien lancé."); }
      if (!response.ok) {
        const detail = Array.isArray(result.detail) ? result.detail.map((item) => item.msg).join(" ") : result.detail;
        throw new Error(detail || `L’analyse n’a pas abouti (HTTP ${response.status}).`);
      }
      if (!result.comparison?.baseline || !result.comparison?.alternative) throw new Error("La réponse ne contient pas les deux hypothèses attendues.");
      state.previous = state.result;
      state.result = result;
      if (result.request) applyPayload(result.request);
      renderResult();
      setDirty(false);
      $("#undo-btn").disabled = !state.previous;
      $("#export-btn").disabled = false;
      resultStatus(result);
    } catch (error) {
      const message = error.name === "AbortError"
        ? "Le délai de réponse est dépassé. Les résultats précédents sont conservés ; vous pouvez relancer un calcul."
        : error.message;
      showMessage(message);
      status("Analyse interrompue · aucun nouveau résultat n’a été validé.", "error");
      if (!state.result) $("#chart-container").innerHTML = '<div class="empty-chart"><p>Le calcul n’a pas abouti. Les données précédentes ne sont pas remplacées.</p></div>';
    } finally {
      clearTimeout(timeout);
      setBusy(false);
    }
  }

  function resultStatus(result) {
    const duration = numeric(result.duration_ms) ? ` · ${number.format(result.duration_ms / 1000)} s` : "";
    if (result.agent?.status === "error") {
      status("Calculs disponibles · l’analyse Bedrock n’a pas abouti.", "error");
      const error = result.agent.error?.message || result.agent.message || "L’agent n’est pas disponible pour cette exécution.";
      showMessage(`${error} Les calculs restent consultables dans le dossier.`);
    } else if (result.agent?.status === "partial") {
      status(`Analyse Bedrock partielle · consulter les actions et limites du dossier${duration}`, "error");
      showMessage(result.agent.message || "L’agent a rencontré une difficulté sur une étape. Consultez les traces avant d’utiliser sa conclusion.");
    } else if (result.mode === "bedrock") {
      status(`Analyse AWS Bedrock terminée · calculs et sources consultables${duration}`);
    } else {
      status(`Comparaison calculée · l’agent Bedrock n’a pas été sollicité${duration}`);
    }
  }

  function metric(label, key, caption) {
    const comparison = state.result.comparison;
    const baseline = comparison.baseline.metrics?.[key];
    const alternative = comparison.alternative.metrics?.[key];
    return `<div class="metric"><span class="metric-label">${escape(label)}</span><div class="metric-values"><span title="Scénario de départ">${escape(pct(baseline))}</span><b aria-hidden="true">→</b><strong title="Hypothèse modifiée">${escape(pct(alternative))}</strong></div><span class="metric-caption">${escape(caption)}</span></div>`;
  }

  function renderResult() {
    $("#metric-grid").innerHTML = [
      metric("Croissance annuelle composée", "cagr_pct", "CAGR historique"),
      metric("Baisse maximale observée", "max_drawdown_pct", "Depuis un sommet précédent"),
      metric("Volatilité annualisée", "volatility_pct", "Variabilité des rendements"),
    ].join("");
    renderChart();
    $("#insight-card").hidden = false;
    $("#summary-title").textContent = state.result.summary?.title || "Une comparaison à examiner.";
    $("#summary-text").textContent = state.result.summary?.text || "";
    $("#insight-mode").textContent = state.result.agent?.status === "partial"
      ? "Analyse Bedrock partielle"
      : state.result.mode === "bedrock" ? "Analyse AWS Bedrock" : "Lecture des calculs";
    const findings = state.result.summary?.findings || [];
    $("#findings-list").innerHTML = findings.map((finding, index) => {
      const refs = (finding.source_ids || []).map((id) => `<button class="source-ref" data-source="${escape(id)}" aria-label="Voir la source ${escape(id)}">${escape(id)}</button>`).join("");
      return `<div class="finding"><span class="finding-number">${String(index + 1).padStart(2, "0")}</span><div class="finding-text">${escape(text(finding))}${refs}</div></div>`;
    }).join("");
    const conditions = state.result.summary?.conditions || [];
    const questions = state.result.profile?.unknown || [];
    $("#revision-conditions").innerHTML = [
      conditions.length ? `<div><h3>Ce qui ferait évoluer l’analyse</h3>${conditions.map((item) => `<p>${escape(text(item))}</p>`).join("")}</div>` : "",
      questions.length ? `<div><h3>À préciser pour aller plus loin</h3>${questions.map((item) => `<p>${escape(text(item))}</p>`).join("")}</div>` : "",
    ].join("");
    const scenarios = state.result.scenarios || [];
    $("#scenario-card").hidden = !scenarios.length;
    $("#stress-scenarios").innerHTML = '<div class="stress-header"><span>Départ</span><span>Hypothèse</span></div>' + scenarios.map((scenario) =>
      `<div class="stress-row"><div><strong>${escape(scenario.name)}</strong><small>${escape(formatDate(scenario.start))} → ${escape(formatDate(scenario.end))}</small></div><div class="stress-number baseline-text">${escape(pct(scenario.baseline_return_pct))}</div><div class="stress-number alternative-text">${escape(pct(scenario.alternative_return_pct))}</div></div>`
    ).join("");
    renderEvidence();
  }

  function renderChart() {
    if (!state.result) return;
    const baseline = state.result.comparison.baseline.series || [];
    const alternative = state.result.comparison.alternative.series || [];
    if (baseline.length < 2 || alternative.length < 2) {
      $("#chart-container").innerHTML = '<div class="empty-chart"><p>Historique insuffisant pour tracer les deux courbes.</p></div>';
      return;
    }
    const transform = (series) => {
      const initial = series[0].value;
      let peak = initial;
      return series.map((point) => {
        peak = Math.max(peak, point.value);
        return { date: point.date, value: state.chart === "value" ? point.value / initial * 100 : numeric(point.drawdown_pct) ? point.drawdown_pct : (point.value / peak - 1) * 100 };
      }).filter((point) => numeric(point.value));
    };
    const b = transform(baseline), a = transform(alternative);
    const data = [...b, ...a].map((point) => point.value);
    const range = Math.max(...data) - Math.min(...data) || 1;
    let min = Math.min(...data) - range * 0.12;
    let max = Math.max(...data) + range * 0.13;
    if (state.chart === "drawdown") max = range * 0.06;
    const width = Math.max($("#chart-container").clientWidth, 300), height = $("#chart-container").clientHeight || 214;
    const padding = { left: 0, right: 39, top: 10, bottom: 23 };
    const w = width - padding.left - padding.right, h = height - padding.top - padding.bottom;
    const x = (index, length = b.length) => padding.left + index / (length - 1) * w;
    const y = (value) => padding.top + (max - value) / (max - min) * h;
    const path = (points) => points.map((point, index) => `${index ? "L" : "M"}${x(index, points.length).toFixed(2)},${y(point.value).toFixed(2)}`).join(" ");
    const area = `${path(a)} L${x(a.length - 1, a.length)},${height - padding.bottom} L0,${height - padding.bottom} Z`;
    let grid = "";
    for (let i = 0; i < 5; i++) {
      const value = min + (max - min) * i / 4;
      const yy = y(value);
      grid += `<line x1="0" y1="${yy}" x2="${w}" y2="${yy}" stroke="#edf1e6" stroke-width="1"/><text class="chart-label" x="${width - 1}" y="${yy + 3}" text-anchor="end">${escape(whole.format(value))}${state.chart === "drawdown" ? "%" : ""}</text>`;
    }
    const indexes = [0, Math.round((b.length - 1) / 4), Math.round((b.length - 1) / 2), Math.round((b.length - 1) * 3 / 4), b.length - 1];
    const dates = indexes.map((index, i) => `<text class="chart-label" x="${x(index)}" y="${height - 1}" text-anchor="${i === 0 ? "start" : i === indexes.length - 1 ? "end" : "middle"}">${escape(String(b[index].date).slice(0, 4))}</text>`).join("");
    const desc = state.chart === "value" ? "Évolution historique de 100 dollars canadiens dans les deux allocations fictives." : "Recul historique de chaque allocation depuis son sommet précédent, en pourcentage.";
    $("#chart-container").innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escape(desc)}"><title>${escape(desc)}</title><defs><linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#99b477" stop-opacity=".15"/><stop offset="100%" stop-color="#99b477" stop-opacity="0"/></linearGradient></defs>${grid}<path d="${area}" fill="url(#chart-fill)"/><path d="${path(b)}" fill="none" stroke="#96abb3" stroke-width="1.6" stroke-linejoin="round"/><path d="${path(a)}" fill="none" stroke="#4c7650" stroke-width="1.9" stroke-linejoin="round"/><line id="chart-cursor" x1="0" y1="${padding.top}" x2="0" y2="${height - padding.bottom}" stroke="#aabc95" stroke-width="1" stroke-dasharray="3 3" visibility="hidden"/><circle id="chart-point-b" r="3.5" fill="#96abb3" stroke="#fff" stroke-width="1.5" visibility="hidden"/><circle id="chart-point-a" r="3.5" fill="#4c7650" stroke="#fff" stroke-width="1.5" visibility="hidden"/>${dates}</svg><div class="chart-tooltip" hidden></div>`;
    $("#chart-subtitle").textContent = state.chart === "value" ? "Valeur de 100 $ simulés · CAD" : "Baisse depuis le sommet observé · %";
    $("#chart-period").textContent = `${formatDate(b[0].date)} — ${formatDate(b[b.length - 1].date)}`;
    const container = $("#chart-container"), tooltip = $(".chart-tooltip");
    container.onpointermove = (event) => {
      const rect = container.getBoundingClientRect();
      const relative = Math.max(0, Math.min(w, event.clientX - rect.left));
      const index = Math.round(relative / w * (b.length - 1));
      const otherIndex = Math.round(relative / w * (a.length - 1));
      const xx = x(index);
      const cursor = $("#chart-cursor");
      cursor.setAttribute("x1", xx); cursor.setAttribute("x2", xx); cursor.setAttribute("visibility", "visible");
      [["b", b[index]], ["a", a[otherIndex]]].forEach(([key, point]) => {
        const circle = $(`#chart-point-${key}`);
        circle.setAttribute("cx", xx); circle.setAttribute("cy", y(point.value)); circle.setAttribute("visibility", "visible");
      });
      const formatter = state.chart === "value" ? money : pct;
      tooltip.innerHTML = `<strong>${escape(formatDate(b[index].date))}</strong><span><i class="baseline"></i>Départ : ${escape(formatter(b[index].value))}</span><span><i class="alternative"></i>Hypothèse : ${escape(formatter(a[otherIndex].value))}</span>`;
      tooltip.hidden = false;
      tooltip.style.left = relative < w * 0.55 ? "auto" : "8px";
      tooltip.style.right = relative < w * 0.55 ? "43px" : "auto";
    };
    container.onpointerleave = () => {
      tooltip.hidden = true;
      ["#chart-cursor", "#chart-point-a", "#chart-point-b"].forEach((id) => $(id)?.setAttribute("visibility", "hidden"));
    };
  }

  function renderEvidence() {
    const result = state.result;
    const sources = result?.sources || state.bootstrap?.sources || [];
    $("#source-count").textContent = sources.length;
    $("#sources-label").textContent = `${sources.length} références consultables`;
    $("#source-list").innerHTML = sources.map((source) => {
      const url = safeUrl(source.url);
      return `<article class="source-item" data-source-id="${escape(source.id)}"><div class="source-meta"><span>${escape(source.publisher || source.kind || source.id)}</span><span class="source-tag">${escape(source.kind || "Source")}</span></div><h3>${escape(source.title)}</h3>${source.as_of ? `<p>Version / consultation : ${escape(source.as_of)}</p>` : ""}${source.reading ? `<p>Niveau de lecture : ${escape(source.reading)}</p>` : ""}<p>${escape(source.note || "")}</p>${url ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">Consulter la source <span aria-hidden="true">↗</span></a>` : ""}</article>`;
    }).join("");
    const limitations = [...(result?.limitations || [])];
    const unknown = result?.profile?.unknown || [];
    const contradictions = result?.profile?.contradictions || [];
    unknown.forEach((item) => limitations.push("À préciser : " + text(item)));
    contradictions.forEach((item) => limitations.push("Tension à examiner : " + text(item)));
    $("#limitations-list").innerHTML = limitations.length
      ? [...new Set(limitations)].map((item) => `<p>${escape(text(item))}</p>`).join("")
      : "<p>Les limites spécifiques seront précisées après une analyse.</p>";
    const trace = result?.trace || [];
    $("#trace-list").innerHTML = trace.length ? trace.map((entry, index) => {
      const labels = { compare_portfolios: "Comparer les allocations", compare_scenario: "Recalculer une hypothèse", profile: "Préciser le contexte", read_evidence: "Consulter les preuves", get_evidence: "Consulter les preuves", bedrock: "Interroger AWS Bedrock", inspect_profile: "Examiner le profil", select_observations: "Sélectionner les résultats", calculate_comparison: "Calculer la comparaison", inspect_comparison: "Examiner les calculs" };
      return `<div class="trace-item ${entry.status === "error" ? "error" : ""}"><span class="trace-circle"></span><div class="trace-title">${escape(labels[entry.tool] || entry.tool || `Étape ${index + 1}`)}</div><p>${escape(text(entry.detail))}</p><small>${escape(entry.status === "error" ? "Erreur" : entry.status === "success" ? "Exécuté" : entry.status || "")}${numeric(entry.duration_ms) ? ` · ${number.format(entry.duration_ms / 1000)} s` : ""}${entry.request_id ? `<br>Requête : ${escape(entry.request_id)}` : ""}</small></div>`;
    }).join("") : '<p class="panel-description">Aucune action d’analyse exécutée pour le moment.</p>';
    const agent = result?.agent;
    if (agent) {
      const model = agent.model || agent.model_id;
      const usage = agent.usage || (agent.calls || []).reduce((sum, call) => ({
        input_tokens: sum.input_tokens + (call.usage?.input_tokens || 0),
        output_tokens: sum.output_tokens + (call.usage?.output_tokens || 0),
        total_tokens: sum.total_tokens + (call.usage?.total_tokens || 0),
      }), { input_tokens: 0, output_tokens: 0, total_tokens: 0 });
      const tokens = usage?.total_tokens || ((usage?.input_tokens || 0) + (usage?.output_tokens || 0));
      $("#agent-detail").innerHTML = `<div class="agent-detail"><strong>${agent.status === "partial" ? "Analyse partielle" : agent.status === "error" ? "Agent indisponible" : "Inférence AWS Bedrock"}</strong>${model ? `Modèle : ${escape(model)}<br>` : ""}${agent.region ? `Région : ${escape(agent.region)}<br>` : ""}${tokens ? `Consommation déclarée : ${whole.format(tokens)} tokens<br>` : ""}${agent.request_id ? `Requête : ${escape(agent.request_id)}<br>` : ""}${escape(agent.error?.message || agent.message || "")}</div>`;
    } else $("#agent-detail").innerHTML = '<div class="agent-detail"><strong>Calcul sans appel de modèle</strong>Les outils numériques ont produit cette comparaison. Le bouton de l’atelier lance une analyse supplémentaire sur AWS Bedrock.</div>';
  }

  async function bootstrap() {
    try {
      const response = await fetch("/api/bootstrap");
      if (!response.ok) throw new Error(`Les sources ne sont pas disponibles (HTTP ${response.status}).`);
      state.bootstrap = await response.json();
      if (!state.bootstrap.personas?.length || !state.bootstrap.assets?.length) throw new Error("L’initialisation ne contient pas les profils et actifs attendus.");
      $("#persona-options").innerHTML = state.bootstrap.personas.map((persona) =>
        `<button class="persona-option" data-persona="${escape(persona.id)}" aria-pressed="false"><span class="persona-avatar">${escape(persona.name.slice(0, 1))}</span><span><strong>${escape(persona.name)}</strong><small>${escape(persona.age)} ans · ${escape(persona.horizon)}</small></span></button>`
      ).join("");
      $$(".persona-option").forEach((button) => button.addEventListener("click", () => selectPersona(button.dataset.persona)));
      renderEvidence();
      selectPersona("robert");
    } catch (error) {
      showMessage(error.message + " Relancez le serveur puis rechargez la page.");
      status("Les données de départ n’ont pas pu être chargées.", "error");
      $("#analyze-btn").disabled = true;
      $("#recalculate-btn").disabled = true;
      $("#chart-container").innerHTML = '<div class="empty-chart"><p>En attente de l’accès aux données du laboratoire.</p></div>';
    }
  }

  document.addEventListener("click", (event) => {
    const nav = event.target.closest("[data-view]");
    if (nav) navigate(nav.dataset.view);
    const source = event.target.closest("[data-source]");
    if (source) navigate("preuves", source.dataset.source);
  });
  $("#analyze-btn").addEventListener("click", () => analyze(true));
  $("#recalculate-btn").addEventListener("click", () => analyze(false));
  $("#reset-btn").addEventListener("click", () => {
    if (!state.bootstrap || state.busy) return;
    navigate("atelier");
    selectPersona(state.persona);
  });
  $("#focus-slider").addEventListener("input", (event) => { updateSlider(event.target.value); setDirty(); });
  $("#focus-weight").addEventListener("input", (event) => { updateSlider(event.target.value); setDirty(); });
  $("#focus-ticker").addEventListener("change", () => { updateBaselineWeight(); setDirty(); });
  ["#prompt", "#horizon", "#capital", "#comfort"].forEach((id) => $(id).addEventListener("input", () => setDirty()));
  $("#add-holding").addEventListener("click", () => {
    const portfolio = readPortfolio();
    const unused = state.bootstrap.assets.find((asset) => !portfolio.some((holding) => holding.ticker === asset.ticker));
    if (!unused) { showMessage("Tous les actifs de l’instantané sont déjà présents."); return; }
    portfolio.push({ ticker: unused.ticker, weight: 0 });
    renderPortfolio(portfolio);
    setDirty();
  });
  $("#undo-btn").addEventListener("click", () => {
    if (!state.previous || state.busy) return;
    const previous = state.previous;
    state.previous = state.result;
    state.result = previous;
    if (previous.request) {
      selectPersona(previous.request.persona, false);
      applyPayload(previous.request);
    }
    renderResult();
    setDirty(false);
    showMessage("");
    resultStatus(previous);
  });
  $("#export-btn").addEventListener("click", () => {
    if (!state.result) return;
    const link = document.createElement("a");
    link.href = `/api/report/${encodeURIComponent(state.result.id)}`;
    link.download = `alphaforge-${state.result.id.slice(0, 8)}.json`;
    link.click();
  });
  $$("[data-chart]").forEach((button) => button.addEventListener("click", () => {
    state.chart = button.dataset.chart;
    $$("[data-chart]").forEach((item) => {
      const active = item.dataset.chart === state.chart;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    renderChart();
  }));
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderChart, 120);
  });
  bootstrap();
})();
