/* AlphaForge — local dossier workbench. No sample outputs or synthetic task states. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const state = {
    examples: [], dossiers: [], snapshot: null, tab: "overview", pending: false,
    pendingRevision: false, polling: null, pollFailures: 0, loadToken: 0,
    displayKeys: new Set(), inspected: null, toastTimer: null, exampleId: null,
  };
  const roles = [
    {id: "agent0", name: "Qualifier", purpose: "Besoin, contraintes et questions utiles."},
    {id: "agent1", name: "Rechercher", purpose: "Sources, méthodes et limites de preuve."},
    {id: "agent2", name: "Résoudre", purpose: "Formulation, calculs et contrôles."},
    {id: "agent3", name: "Restituer", purpose: "Explication, alternatives et révisions."},
  ];
  const statuses = {
    pending: ["En attente", "neutral"], queued: ["Planifié", "neutral"], ready: ["Prêt", "neutral"],
    running: ["En cours", "running"], started: ["En cours", "running"], active: ["En cours", "running"],
    complete: ["Terminé", "success"], completed: ["Terminé", "success"], success: ["Réussi", "success"],
    succeeded: ["Réussi", "success"], committed: ["Enregistré", "success"], passed: ["Satisfait", "success"],
    pass: ["Satisfait", "success"], sufficient: ["Suffisant", "success"], conditional: ["Sous conditions", "warning"],
    partial: ["Partiel", "warning"], waiting: ["En attente", "warning"], waiting_input: ["Précision requise", "warning"],
    awaiting_input: ["Précision requise", "warning"], blocked: ["Bloqué", "warning"], paused: ["En pause", "warning"],
    failed: ["Échec", "error"], error: ["Erreur", "error"], rejected: ["Rejeté", "error"],
    missing_input: ["Entrées manquantes", "warning"], unsupported: ["Hors domaine", "warning"],
    infeasible: ["Infaisable dans le modèle", "warning"], stale: ["Ancienne portée", "warning"],
    invalidated: ["À réexaminer", "warning"], cancelled: ["Annulé", "neutral"],
    superseded: ["Remplacé", "neutral"], reused: ["Réutilisé", "purple"],
    not_examined: ["Non examiné", "neutral"], not_applicable: ["Non applicable", "neutral"],
    insufficient: ["Insuffisant", "warning"], resolved: ["Résolu", "success"],
    sufficient_with_reservation: ["Suffisant sous réserve", "warning"],
    not_established: ["Non établie", "warning"],
    not_started: ["Aucune tâche", "neutral"],
    resolved_conditionally: ["Résolu sous condition", "warning"], open: ["Ouvert", "warning"],
    outcome_unknown: ["Issue inconnue", "warning"], unavailable: ["Indisponible", "warning"],
  };
  const labels = {
    capital_cad: "Capital initial", withdrawal_cad: "Retrait", withdrawal_months: "Échéance du retrait",
    horizon_years: "Horizon du solde", currency: "Devise", decision_type: "Type de décision",
    objective: "Critère", reserve_policy: "Réserve", knowledge_date: "Date de connaissance",
    scenario_loss_limit_cad: "Budget de perte par scénario", comparison: "Comparaison",
    reserve_allocation: "Financer un retrait", historical_comparison: "Comparer un historique",
    explanation: "Question pédagogique", unsupported: "Demande hors domaine admis",
    minimize_reallocated_capital: "Minimiser le capital réalloué", compare_historical: "Comparaison historique",
    explain: "Expliquer", unknown: "Non précisé", abstract_nominal: "Réserve nominale abstraite",
    real_instrument_unknown: "Instrument réel non qualifié", holdings: "Positions initiales",
    max_asset_weights: "Plafonds de poids", scenarios: "Scénarios", assumptions: "Hypothèses",
    turnover_cad: "Capital réalloué", reallocated_capital_cad: "Capital réalloué",
    turnover_pct: "Capital réalloué / capital initial", minimum_turnover: "Minimum de capital réalloué",
    loss_cad: "Perte", wealth_before_withdrawal_cad: "Avant retrait",
    wealth_after_withdrawal_cad: "Après retrait", horizon_months: "Échéance",
    constraints: "Contraintes du modèle", independent_lower_bound: "Borne indépendante",
    multiple_optima: "Solutions multiples", calendar_fx: "Calendrier et change",
    snapshot_availability: "Disponibilité des données", adjustments: "Ajustements des prix",
    reallocated_cad: "Capital réalloué", turnover: "Capital réalloué / capital initial",
    reserve_cad: "Réserve", max_scenario_loss_cad: "Plus forte perte des scénarios",
    remaining_value_cad: "Capital restant", ending_value_cad: "Valeur finale",
    initial_value_cad: "Capital initial",
    total_return_pct: "Rendement cumulé", cagr_pct: "Rendement annualisé",
    volatility_pct: "Volatilité annualisée", max_drawdown_pct: "Repli maximal",
    fidelity: "Fidélité de restitution", exactness: "Exactitude du calcul",
    arithmetic: "Exactitude du calcul", mandate: "Adéquation au mandat",
    documentary_grounding: "Ancrage documentaire",
    computational_accuracy: "Exactitude du calcul", accuracy: "Exactitude du calcul",
    suitability: "Adéquation au mandat", adequacy: "Adéquation au mandat",
    grounding: "Ancrage documentaire", external_validity: "Validité externe et portée",
    declared: "Déclaré", assumed: "Hypothèse", extracted: "Extrait d’une source",
    hypothetical: "Scénario hypothétique", historical: "Historique observé",
    metadata: "Métadonnées", abstract: "Résumé", excerpt: "Passage ciblé",
    full_text: "Texte intégral", targeted: "Passages ciblés",
    document_metadata: "Métadonnées", targeted_passages: "Passages ciblés",
    human: "Déclaration humaine", browser: "Présentation", request_received: "Demande reçue",
    revision_requested: "Correction reçue", changes_committed: "Pièces enregistrées",
    view_displayed: "Vue effectivement affichée", role_committed: "Contribution enregistrée",
    conditional_optimality: "Optimalité conditionnelle", numerical_witness: "Témoin numérique",
    historical_observation: "Observation historique", limitation: "Limite",
    reserve: "Réserve", budget: "Budget", RESERVE_ABSTRAITE: "Réserve abstraite",
    name: "Fenêtre", start: "Début", end: "Fin",
  };
  const palette = ["#b8ca82", "#537b5b", "#90a5a5", "#c1b7cb", "#b38d65", "#5c6970", "#879356"];
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const array = (value) => Array.isArray(value) ? value : [];
  const object = (value) => value && typeof value === "object" && !Array.isArray(value) ? value : {};
  const text = (value) => typeof value === "string" ? value : value == null ? "" : typeof value === "number" || typeof value === "boolean" ? String(value) : JSON.stringify(value);
  const title = (value) => labels[value] || (String(value).startsWith("asset_cap:") ? `Plafond ${String(value).slice(10)}` : String(value).startsWith("scenario_loss:") ? `Perte du scénario ${String(value).slice(14)}` : String(value || "Non précisé").replace(/_/g, " "));
  const number = (value, maximumFractionDigits = 2) => typeof value === "number" && Number.isFinite(value) ? new Intl.NumberFormat("fr-CA", {maximumFractionDigits}).format(value) : "—";
  const money = (value) => typeof value === "number" ? `${number(value)} CAD` : "Non précisé";
  const badge = (value) => { const item = statuses[value] || [title(value), "neutral"]; return `<span class="badge ${item[1]}">${escape(item[0])}</span>`; };
  const raw = (value) => `<pre class="json">${escape(JSON.stringify(value, null, 2))}</pre>`;
  const content = (value) => object(value?.content ?? value);
  const currentWrapper = (value) => value && value.usable !== false ? value : null;
  const currentAnalysis = () => currentWrapper(state.snapshot?.current_analysis);
  const currentView = () => state.pendingRevision ? null : currentWrapper(state.snapshot?.current_view);
  const latestRun = () => array(state.snapshot?.runs).at(-1) || {};
  const isRunning = () => array(state.snapshot?.runs).some((run) => ["running", "queued", "pending", "active"].includes(run.status));
  const roleName = (id) => { const role = roles.find((item) => item.id === id); return role ? `Agent ${roles.indexOf(role)} · ${role.name}` : title(id); };
  const refOf = (artifact) => artifact?.ref || (artifact?.id && artifact?.version != null ? `${artifact.id}@${artifact.version}` : null);
  const date = (value) => { const parsed = new Date(value); return value && !Number.isNaN(parsed.valueOf()) ? new Intl.DateTimeFormat("fr-CA", {dateStyle:"short", timeStyle:"short"}).format(parsed) : value || "Date non fournie"; };
  const shortId = (id) => id ? String(id).length > 16 ? `${String(id).slice(0, 8)}…${String(id).slice(-4)}` : String(id) : "";
  const safeUrl = (url) => { if(typeof url !== "string" || !/^https?:\/\//i.test(url.trim()))return null; try { const parsed = new URL(url); return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null; } catch { return null; } };
  const listText = (items) => (typeof items === "string" ? [items] : array(items)).map((item) => {
    if(typeof item === "string" && item.startsWith("{")){try{const parsed=JSON.parse(item);return parsed.message || parsed.reason || parsed.description || item;}catch{return item;}}
    return typeof item === "object" ? item.text || item.description || item.message || item.reason || item.question || JSON.stringify(item) : item;
  }).filter(Boolean);
  const limitations = (...values) => [...new Set(values.flatMap(listText))];
  const limitBox = (items, heading = "Portée et limites") => items.length ? `<div class="limit-box"><h3>${escape(heading)}</h3><ul>${items.map((item) => `<li>${escape(item)}</li>`).join("")}</ul></div>` : "";
  const inspectButton = (ref, label = "Inspecter la pièce") => ref ? `<button type="button" class="text-button" data-inspect-ref="${escape(ref)}">${escape(label)} ↗</button>` : "";
  const jsonButton = (key, label = "Données structurées") => `<button type="button" class="text-button" data-inspect-key="${escape(key)}">${escape(label)} ↗</button>`;
  const refButtons = (refs) => array(refs).map((ref) => {
    if (ref?.pointer) return `<button class="inline-ref" data-result-pointer="${escape(ref.pointer)}" type="button">Valeur liée ↗</button>`;
    const id = typeof ref === "string" ? ref : refOf(ref) || ref.id || ref.source_ref;
    if(id?.startsWith("$"))return `<span class="ref-chip" title="Alias de production conservé tel que reçu ; version non résolue">${escape(id)} · alias</span>`;
    return id ? `<button class="inline-ref" data-inspect-ref="${escape(id)}" type="button">${escape(id)}</button>` : "";
  }).join("");
  function errorMessage(error) {
    if (typeof error === "string") return error;
    if (Array.isArray(error)) return error.map((item) => item.msg || text(item)).join(" · ");
    return error?.message || error?.detail || error?.code || (error ? text(error) : "Erreur sans diagnostic fourni.");
  }
  async function api(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(path, {cache:"no-store", ...options, signal:controller.signal, headers:{"Content-Type":"application/json", ...options.headers}});
      const payload = await response.json().catch(() => ({}));
      setConnection(true);
      if (!response.ok) { const error = new Error(response.status === 404 && payload.detail === "Not Found" ? "Le service des dossiers n’est pas disponible à cette adresse. Utilisez Actualiser après le démarrage de l’API." : text(errorMessage(payload.detail || payload.error || payload)) || `Erreur HTTP ${response.status}`); error.status = response.status; error.payload = payload; throw error; }
      return payload;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("Le serveur n’a pas répondu dans les 30 secondes. L’opération peut encore être en cours ; actualisez le dossier avant de la relancer.");
      if (!error.status) setConnection(false);
      throw error;
    } finally { clearTimeout(timeout); }
  }
  function setConnection(connected) {
    $("connection").classList.toggle("offline", !connected);
    $("connection").innerHTML = `<span class="dot"></span> ${connected ? "Serveur local connecté" : "Connexion interrompue"}`;
  }
  function showError(message) { $("global-error").textContent = message; $("global-error").hidden = !message; }
  function toast(message) { clearTimeout(state.toastTimer); $("toast").textContent = message; $("toast").hidden = false; state.toastTimer = setTimeout(() => { $("toast").hidden = true; }, 5500); }
  function setPending(value) {
    state.pending = value;
    $("create-submit").disabled = value;
    $("revise-submit").disabled = value;
    $("new-dossier").disabled = value;
    $("export").setAttribute("aria-disabled",String(value));
    document.querySelectorAll("[data-resume]").forEach((button) => { button.disabled = value; });
  }
  async function loadLibrary() {
    const result = await api("/api/dossiers");
    state.dossiers = array(result.dossiers);
    renderLibrary();
  }
  function renderLibrary() {
    $("dossier-count").textContent = state.dossiers.length;
    $("dossier-list").innerHTML = state.dossiers.length ? state.dossiers.map((dossier) => `<button type="button" class="dossier-item ${dossier.id === state.snapshot?.id ? "active" : ""}" data-open-dossier="${escape(dossier.id)}"><strong>${escape(dossier.title || "Demande sans titre")}</strong><small><span>r${escape(dossier.revision ?? "—")}</span><span>${escape(statuses[dossier.status]?.[0] || title(dossier.status))}</span></small></button>`).join("") : '<p class="sidebar-empty">Vos dossiers apparaîtront ici.</p>';
  }
  function renderExamples() {
    $("examples").innerHTML = state.examples.length ? state.examples.map((example, index) => `<button class="example-button" type="button" data-example="${escape(example.id)}"><span class="example-num">CAS ${String(index + 1).padStart(2,"0")} · ENTRÉES FICTIVES</span><strong>${escape(example.title)}</strong><p>${escape(example.description || example.prompt?.slice(0, 145) || "")}${!example.description && example.prompt?.length > 145 ? "…" : ""}</p><span class="example-link">Charger et adapter <span aria-hidden="true">↗</span></span></button>`).join("") : '<p class="muted">Aucun exemple disponible. Vous pouvez formuler votre demande.</p>';
  }
  function fillFacts(facts) {
    $("facts-json").value = JSON.stringify(facts || {}, null, 2);
    document.querySelectorAll("[data-fact]").forEach((input) => { input.value = facts?.[input.dataset.fact] ?? ""; });
  }
  function openExample(id) {
    const example = state.examples.find((item) => item.id === id);
    if (!example) return;
    state.exampleId = id;
    $("prompt").value = example.prompt || "";
    fillFacts(example.facts || {});
    $("example-note").hidden = false;
    $("example-note").textContent = `« ${example.title} » : entrées fictives chargées, modifiables avant lancement. Aucun résultat n’a encore été calculé.`;
    $("prompt").focus();
    toast("Exemple chargé. Relisez ou adaptez les entrées, puis ouvrez le dossier.");
  }
  function newDossier() {
    clearTimeout(state.polling);
    state.loadToken += 1;
    state.snapshot = null;
    state.pendingRevision = false;
    state.exampleId = null;
    setTab("overview");
    $("start-view").hidden = false;
    $("dossier-view").hidden = true;
    $("breadcrumb-current").textContent = "Nouvelle demande";
    $("prompt").value = "";
    fillFacts({});
    $("example-note").hidden = true;
    showError("");
    history.replaceState(null, "", location.pathname);
    renderLibrary();
    window.scrollTo({top:0, behavior:"smooth"});
  }
  function parseObject(value, label) {
    let parsed;
    try { parsed = JSON.parse(value || "{}"); } catch { throw new Error(`${label} : JSON invalide. Utilisez des guillemets doubles et vérifiez les virgules.`); }
    if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") throw new Error(`${label} : un objet JSON est requis, par exemple {"withdrawal_cad": 40000}.`);
    return parsed;
  }
  async function createDossier(event) {
    event.preventDefault();
    if (state.pending) return;
    let facts;
    try {
      facts = parseObject($("facts-json").value, "Entrées structurées");
      document.querySelectorAll("[data-fact]").forEach((input) => {
        if (input.value !== "") facts[input.dataset.fact] = Number(input.value);
        else delete facts[input.dataset.fact];
      });
    } catch (error) { showError(error.message); return; }
    const prompt = $("prompt").value.trim();
    if (!prompt) { showError("Décrivez votre demande avant d’ouvrir un dossier."); return; }
    showError(""); setPending(true);
    $("create-submit").innerHTML = 'Création du dossier… <span aria-hidden="true">↗</span>';
    try {
      const result = await api("/api/dossiers", {method:"POST", body:JSON.stringify({prompt, facts, use_ai:$("use-ai").checked})});
      const snapshot = result.dossier || result.snapshot || result;
      const id = snapshot.id || result.dossier_id;
      if (!id) throw new Error("Le serveur n’a pas renvoyé l’identifiant du dossier. Actualisez la bibliothèque avant de réessayer.");
      await openDossier(id);
      await loadLibrary();
    } catch (error) { showError(error.message); }
    finally { setPending(false); $("create-submit").innerHTML = 'Ouvrir le dossier <span aria-hidden="true">↗</span>'; }
  }
  async function openDossier(id) {
    const token = ++state.loadToken;
    clearTimeout(state.polling);
    showError("");
    try {
      const snapshot = await api(`/api/dossiers/${encodeURIComponent(id)}`);
      if (token !== state.loadToken) return;
      state.snapshot = snapshot;
      state.pendingRevision = false;
      state.pollFailures = 0;
      $("revision-message").value = "";
      $("revision-withdrawal").value = "";
      $("changes-json").value = "{}";
      document.querySelector('input[name="intent"][value="replace"]').checked = true;
      history.replaceState(null, "", `${location.pathname}?dossier=${encodeURIComponent(id)}`);
      renderDossier();
      renderLibrary();
      schedulePoll();
    } catch (error) { if (token === state.loadToken) showError(error.message); }
  }
  function schedulePoll(delay = 1600) {
    clearTimeout(state.polling);
    if (!state.snapshot) return;
    state.polling = setTimeout(poll, document.hidden ? 7000 : delay);
  }
  async function poll() {
    const id = state.snapshot?.id, token = state.loadToken;
    if (!id) return;
    try {
      const snapshot = await api(`/api/dossiers/${encodeURIComponent(id)}`);
      if (token !== state.loadToken || state.snapshot?.id !== id) return;
      // A GET started before an admitted correction cannot restore its old view.
      if (Number(snapshot.revision) < Number(state.snapshot.revision)) { schedulePoll(500); return; }
      if(state.pollFailures && $("global-error").textContent.startsWith("Actualisation interrompue"))showError("");
      state.pollFailures = 0;
      const changed = JSON.stringify(snapshot) !== JSON.stringify(state.snapshot);
      state.snapshot = snapshot;
      if (changed) { renderDossier(); state.dossiers = state.dossiers.map((item) => item.id === id ? {...item, title:snapshot.title, revision:snapshot.revision, status:snapshot.status} : item); renderLibrary(); }
      schedulePoll(isRunning() ? 1600 : 6500);
    } catch (error) {
      if (token !== state.loadToken) return;
      state.pollFailures += 1;
      showError(`Actualisation interrompue : ${error.message} Les dernières données reçues restent visibles avec leur version.`);
      schedulePoll(Math.min(12000, 2500 * state.pollFailures));
    }
  }
  async function reviseDossier(event) {
    event.preventDefault();
    if (state.pending || !state.snapshot) return;
    let changes;
    try {
      changes = parseObject($("changes-json").value, "Changements structurés");
      if ($("revision-withdrawal").value !== "") changes.withdrawal_cad = Number($("revision-withdrawal").value);
    } catch (error) { showError(error.message); return; }
    let message = $("revision-message").value.trim();
    if (!message && !Object.keys(changes).length) { showError("Ajoutez une précision, une question ou un changement avant d’envoyer la révision."); return; }
    const intent = document.querySelector('input[name="intent"]:checked').value;
    if (!message && changes.withdrawal_cad != null) message = `${intent === "variant" ? "Explorer une variante avec" : "Corriger le besoin avec"} un retrait de ${changes.withdrawal_cad} CAD.`;
    if (!message) message = `${intent === "variant" ? "Explorer une variante avec" : "Appliquer"} les changements structurés explicitement renseignés.`;
    const id = state.snapshot.id, token = state.loadToken;
    showError(""); setPending(true); state.pendingRevision = true;
    renderOverview();
    $("revise-submit").innerHTML = 'Envoi de la révision… <span aria-hidden="true">↗</span>';
    try {
      const result = await api(`/api/dossiers/${encodeURIComponent(id)}/revise`, {method:"POST", body:JSON.stringify({message, changes, intent, base_revision:state.snapshot.revision})});
      if (token !== state.loadToken) return;
      const snapshot = result.dossier || result.snapshot || result;
      const newId = snapshot.id || result.dossier_id || id;
      state.pendingRevision = false;
      if (snapshot.id && Object.hasOwn(snapshot, "active_problem")) {
        state.snapshot = snapshot;
        $("revision-message").value = ""; $("revision-withdrawal").value = ""; $("changes-json").value = "{}";
        history.replaceState(null, "", `${location.pathname}?dossier=${encodeURIComponent(newId)}`);
        renderDossier();
        schedulePoll();
      } else { await openDossier(newId); }
      await loadLibrary();
      toast(intent === "variant" ? "Variante enregistrée. Consultez sa portée et ses résultats." : "Correction enregistrée. Les résultats dépendants sont en cours de réexamen.");
    } catch (error) {
      state.pendingRevision = false;
      showError(`${error.status === 409 ? "Le dossier a évolué pendant votre saisie. Votre texte est conservé ; examinez la révision active avant de renvoyer. " : ""}${error.message}`);
      await poll();
      renderDossier();
    } finally { state.pendingRevision = false; setPending(false); $("revise-submit").innerHTML = 'Envoyer la révision <span aria-hidden="true">↗</span>'; }
  }
  async function resume() {
    if (!state.snapshot || state.pending) return;
    setPending(true); showError("");
    try {
      const id = state.snapshot.id;
      await api(`/api/dossiers/${encodeURIComponent(id)}/resume`, {method:"POST", body:"{}"});
      await poll();
      toast("Demande de reprise envoyée. L’activité ci-dessous indique les travaux réellement repris.");
    } catch (error) { showError(error.message); }
    finally { setPending(false); }
  }
  function renderDossier() {
    if (!state.snapshot) return;
    const dossier = state.snapshot;
    $("start-view").hidden = true; $("dossier-view").hidden = false;
    const activeTitle=content(currentView()).title || (dossier.active_problem?.decision_type ? title(dossier.active_problem.decision_type) : dossier.comparison ? "Révision du dossier en cours" : "Votre demande en cours de qualification");
    $("breadcrumb-current").textContent = activeTitle;
    $("dossier-title").textContent = activeTitle;
    $("dossier-short-id").textContent = shortId(dossier.id);
    $("revision-badge").textContent = `Révision ${dossier.revision ?? "—"}`;
    $("dossier-subtitle").textContent = `${statuses[dossier.status]?.[0] || title(dossier.status)}${latestRun().request?.use_ai === false ? " · Mode déterministe, sans inférence de modèle" : ""} · ${dossier.id}`;
    $("export").href = `/api/dossiers/${encodeURIComponent(dossier.id)}/export`;
    $("export").download = `AlphaForge_${dossier.id}_r${dossier.revision}.json`;
    renderRunNotice(); renderRoles(); renderOverview(); renderMandate(); renderEvidence(); renderActivity(); renderHistory(); renderContext(); renderQuestions(); renderRoute();
    markDisplayed();
  }
  function renderRunNotice() {
    const run = latestRun(), error = run.error;
    const notice = $("run-notice");
    const status = state.snapshot.status;
    if (error || ["error","failed","paused","interrupted"].includes(run.status)) {
      notice.hidden = false; notice.className = "notice error";
      notice.innerHTML = `<strong>${escape(run.status === "paused" ? "Exécution en pause." : "L’exécution demande une reprise.")}</strong> ${escape(errorMessage(error))}<button class="button secondary" data-resume type="button">Reprendre le dossier</button>${error && typeof error === "object" ? `<details><summary>Diagnostic conservé</summary>${raw(error)}</details>` : ""}`;
    } else if (isRunning()) {
      notice.hidden = false; notice.className = "notice";
      notice.innerHTML = `<span class="loading-dot" aria-hidden="true"></span><strong>Travail en cours.</strong> ${run.current_role ? `${escape(roleName(run.current_role))} intervient sur le dossier.` : "L’exécution est enregistrée ; ses étapes apparaissent dans l’activité réelle."} Les pièces s’affichent à mesure qu’elles deviennent disponibles.`;
    } else if (["missing_input","waiting_input","awaiting_input","blocked","waiting"].includes(status)) {
      notice.hidden = false; notice.className = "notice";
      notice.innerHTML = '<strong>Une précision ou une pièce manque pour conclure.</strong> Les questions ouvertes indiquent ce qui reste à établir.';
    } else { notice.hidden = true; }
  }
  function renderRoles() {
    const artifacts = array(state.snapshot.artifacts), tasks = array(state.snapshot.tasks), attempts = array(state.snapshot.attempts);
    $("roles").innerHTML = roles.map((role, index) => {
      const ownTasks = tasks.filter((task) => task.role === role.id);
      const task = ownTasks.findLast((item) => ["running","started","active"].includes(item.status)) || ownTasks.at(-1);
      const ownArtifacts = artifacts.filter((item) => item.owner === role.id);
      const ownAttempts = attempts.filter((item) => item.role === role.id);
      const stateName = task?.status || (ownArtifacts.length ? "committed" : "not_started");
      return `<button class="role-card" type="button" data-role="${role.id}" data-state="${escape(stateName)}" aria-label="${escape(roleName(role.id))}, ${escape(statuses[stateName]?.[0] || title(stateName))}"><div class="role-top"><span class="role-number">${index}</span>${badge(stateName)}</div><h3>${role.name}</h3><p>${role.purpose}</p><div class="role-footer"><span>${ownArtifacts.length} pièce${ownArtifacts.length > 1 ? "s" : ""}</span><span>${ownAttempts.filter((item) => item.request_id).length} reçu${ownAttempts.filter((item) => item.request_id).length > 1 ? "s" : ""} AWS ↗</span></div></button>`;
    }).join("");
  }
  function renderOverview() {
    const viewWrapper = currentView(), analysisWrapper = state.pendingRevision ? null : currentAnalysis();
    const view = content(viewWrapper), analysis = content(analysisWrapper);
    let html = "";
    if (viewWrapper) {
      const claims = array(view.claims);
      html += `<section class="panel content-panel answer-panel"><div class="section-heading"><div><p class="eyebrow">RÉPONSE À EXAMINER · AGENT 3</p><h2>${escape(view.title || "Ce que le dossier permet de dire")}</h2></div>${badge(view.status || analysis.status || "partial")}</div>${view.summary ? `<p class="answer-summary">${escape(text(view.summary))}</p>` : ""}
        ${claims.length ? `<div class="claims">${claims.map((claim,index) => `<div class="claim"><span class="claim-number">${String(index + 1).padStart(2,"0")}</span><div class="claim-copy">${escape(claim.text || text(claim))}${refButtons(claim.result_refs || claim.source_refs || claim.evidence_refs)}${claim.kind ? `<span class="claim-kind">${escape(title(claim.kind))}</span>` : ""}</div></div>`).join("")}</div>` : ""}
        ${listText(view.explanation).length ? `<details class="answer-details"><summary>Développer l’explication</summary>${listText(view.explanation).map((item) => `<p>${escape(item)}</p>`).join("")}</details>` : ""}
        ${limitBox(limitations(view.calculation_limitations || view.limitations, analysis.limitations, state.snapshot.limitations))}
        ${view.documentary_limitations?.length ? `<p class="muted">Ces réserves documentaires sont des commentaires de revue ; elles ne constituent pas des résultats du calcul. Les contrôles et reçus Agent 2 ci-dessous indiquent ce qui a été établi ensuite.</p>${limitBox(limitations(view.documentary_limitations), "Observations à la revue Agent 1, avant le calcul")}` : ""}
        <div class="detail-bar"><span>${escape(refOf(viewWrapper) || "Vue courante")} · Affichée, sans accord implicite</span>${inspectButton(refOf(viewWrapper), "Examiner les liens et citations")}</div></section>`;
    } else {
      const pending = state.pendingRevision || isRunning();
      html += `<section class="empty-panel"><span class="empty-symbol" aria-hidden="true">${pending ? "◌" : "◎"}</span><p class="eyebrow">${state.pendingRevision ? "CORRECTION EN COURS D’ENVOI" : "RESTITUTION NON DISPONIBLE"}</p><h2>${state.pendingRevision ? "Les conclusions précédentes sont mises de côté." : pending ? "Le dossier se construit." : "La réponse reste à établir."}</h2><p>${state.pendingRevision ? "La correction doit être enregistrée puis les dépendances réexaminées. L’historique conserve les résultats dans leur ancien contexte." : pending ? "Vous pouvez déjà examiner le besoin, les questions et les pièces disponibles. Aucune réponse finale n’est présentée avant sa production." : "Consultez les précisions attendues, les limites et les diagnostics de l’activité. Un calcul disponible ci-dessous ne constitue pas à lui seul une restitution validée."}</p></section>`;
    }
    if (analysisWrapper) {
      html += renderAnalysis(analysis, analysisWrapper);
    }
    const checks = view.controls || view.verification || null;
    if (checks) html += renderChecks(checks, "Les contrôles de restitution", "view-checks");
    if (!viewWrapper && !analysisWrapper && limitations(state.snapshot.limitations).length) html += `<section class="panel content-panel"><h2 class="small-heading">Limites déjà identifiées</h2>${limitBox(limitations(state.snapshot.limitations))}</section>`;
    $("overview").innerHTML = html;
  }
  function renderAnalysis(analysis, wrapper) {
    const options = array(analysis.options);
    const method = object(analysis.method);
    return `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">ANALYSE COMPUTATIONNELLE · AGENT 2</p><h2>${analysis.inputs?.decision_type === "historical_comparison" || state.snapshot.active_problem?.decision_type === "historical_comparison" ? "Comparer les trajectoires" : "Examiner les possibilités"}</h2></div>${badge(analysis.status || "partial")}</div>
      ${method.label || method.name || method.id ? `<p class="field-help" style="margin:0 0 18px">Méthode : ${escape(method.label || method.name || method.id)}${method.version ? ` · ${escape(method.version)}` : ""}</p>` : ""}
      ${renderHistoryChart(options, method.metadata)}
      ${options.length ? `<div class="option-grid ${options.length === 2 ? "two-options" : ""}">${options.map((option,index) => renderOption(option,index)).join("")}</div>` : `<p class="empty-note">${escape(analysis.message || (analysis.status === "infeasible" ? "Aucune option admissible dans le modèle actuel. Les contraintes actives n’ont pas été assouplies." : "Aucune allocation ou comparaison disponible avec ces entrées."))}</p>`}
      ${limitBox(limitations(analysis.missing), "Entrées ou preuves manquantes")}
      ${limitBox(limitations(analysis.limitations))}
      <div class="detail-bar"><span>${escape(refOf(wrapper) || "Analyse courante")}</span>${inspectButton(refOf(wrapper), "Examiner méthode, entrées et valeurs")}</div></section>
      ${analysis.checks ? renderChecks(analysis.checks, "Contrôles du calcul", "analysis-checks") : ""}`;
  }
  function weightEntries(weights) {
    if (Array.isArray(weights)) return weights.map((item) => [item.ticker || item.asset || item.label, item.weight ?? item.value]).filter(([,value]) => typeof value === "number");
    return Object.entries(object(weights)).filter(([,value]) => typeof value === "number");
  }
  function renderAllocation(weights, label) {
    const entries = weightEntries(weights);
    if (!entries.length) return "";
    let cursor = 0;
    const rects = entries.map(([asset,weight],index) => { const x = cursor; cursor += Math.max(0,weight * 100); return `<rect x="${x}" y="0" width="${Math.max(0,weight * 100)}" height="12" fill="${palette[index % palette.length]}"><title>${escape(title(asset))} : ${number(weight * 100)} %</title></rect>`; }).join("");
    return `<svg class="allocation-chart" viewBox="0 0 100 12" preserveAspectRatio="none" role="img" aria-label="${escape(label)} : ${escape(entries.map(([asset,weight]) => `${title(asset)} ${number(weight * 100)} %`).join(", "))}">${rects}</svg><div class="allocation-legend">${entries.map(([asset,weight],index) => `<span><i style="background:${palette[index % palette.length]}"></i>${escape(title(asset))} ${number(weight * 100)} %</span>`).join("")}</div>`;
  }
  function metricValue(value, key) {
    if (value && typeof value === "object" && Object.hasOwn(value, "value")) return {value:value.value, unit:value.unit === "percent" ? "%" : value.unit || "", label:value.label || title(key)};
    return {value, unit:key.endsWith("_cad") ? "CAD" : key.endsWith("_pct") ? "%" : "", label:title(key)};
  }
  function renderOption(option, index) {
    const metrics = object(option.metrics);
    const historicalKeys=["total_return_pct","cagr_pct","ending_value_cad","max_drawdown_pct","volatility_pct","initial_value_cad"];
    const entries=Object.hasOwn(metrics,"total_return_pct") || array(option.series).length ? historicalKeys.filter((key)=>Object.hasOwn(metrics,key)).map((key)=>[key,metrics[key]]) : Object.entries(metrics);
    const simple = entries.filter(([,value]) => typeof value === "number" || value && typeof value === "object" && typeof value.value === "number").slice(0,6);
    return `<article class="option-card"><h3>${escape(option.label || option.name || `Option ${index + 1}`)}</h3>${typeof option.admissible === "boolean" ? `<span class="badge ${option.admissible ? "success" : "warning"}">${option.admissible ? "Admissible dans le périmètre contrôlé" : "Contraintes non respectées"}</span>` : option.status ? badge(option.status) : ""}${option.description ? `<p>${escape(option.description)}</p>` : ""}
      ${renderAllocation(option.weights || option.portfolio, option.label || `Option ${index + 1}`)}
      ${simple.length ? `<div class="option-metrics">${simple.map(([key,value]) => { const metric=metricValue(value,key); return `<div class="option-metric"><span>${escape(metric.label)}</span><strong>${number(metric.value)}<small>${escape(metric.unit)}</small></strong></div>`; }).join("")}</div>` : ""}
      ${option.scenario_results || option.scenarios ? renderScenarioTable(option.scenario_results || option.scenarios) : ""}
      ${array(option.violations).length ? `<div class="limit-box"><h3>Contraintes en échec</h3><ul>${option.violations.map((item) => `<li>${escape(title(item.constraint || item.id || text(item)))}${typeof item.residual === "number" ? ` · résidu ${number(item.residual,6)} ${escape(item.unit || "")}` : ""}</li>`).join("")}</ul></div>` : ""}
      ${option.admissibility_scope ? `<p class="reduced-note">${escape(option.admissibility_scope)}</p>` : ""}
      ${limitBox(limitations(option.limitations), "Limite de cette option")}
      <details class="metric-details"><summary>Toutes les valeurs et contrôles de cette option</summary>${raw(option)}</details></article>`;
  }
  function renderScenarioTable(scenarios) {
    if (!Array.isArray(scenarios) || !scenarios.length) return "";
    const keys = scenarios.some((item)=>item.loss_cad != null) ? ["label","loss_cad","wealth_after_withdrawal_cad"] : ["name","start","end","total_return_pct","max_drawdown_pct","ending_value_cad"].filter((key)=>scenarios.some((item)=>Object.hasOwn(item,key)));
    const units = (key)=>key.endsWith("_cad")?" (CAD)":key.endsWith("_pct")?" (%)":"";
    return `<p class="field-help" style="margin-top:15px">${scenarios.some((item)=>item.kind === "hypothetical") ? "Chocs hypothétiques sans probabilité. Le retrait n’est pas une perte de marché." : "Fenêtres historiques : allocations réinitialisées au début de chaque fenêtre."}</p><div class="table-wrap" style="margin-top:8px"><table class="data-table"><thead><tr>${keys.map((key) => `<th>${escape(key==="label"?"Scénario":title(key))}${units(key)}</th>`).join("")}</tr></thead><tbody>${scenarios.map((item) => `<tr>${keys.map((key) => `<td>${escape(item[key] == null ? "—" : typeof item[key] === "number" ? number(item[key]) : text(item[key]))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  }
  function renderHistoryChart(options, metadata) {
    const available=options.filter((item)=>array(item.series).length>1).slice(0,4);
    if (!available.length) return "";
    const series=available.map((item)=>({label:item.label || item.name,points:item.series.map((point)=>({date:point.date,value:point.value ?? point.value_cad})).filter((point)=>typeof point.value==="number")}));
    if(series.some((item)=>item.points.length<2))return"";
    const values=series.flatMap((item)=>item.points.map((point)=>point.value));
    const min=Math.min(...values),max=Math.max(...values),span=max-min || 1;
    const colors=["#8da5aa","#4b7142","#987b5e","#897195"];
    const x=(index,len)=>100+index/(len-1)*558, y=(value)=>185-(value-min)/span*155;
    const axisValue=(value)=>new Intl.NumberFormat("fr-CA",{notation:"compact",maximumFractionDigits:1}).format(value);
    const lines=series.map((item,index)=>`<path d="${item.points.map((point,i)=>`${i?"L":"M"}${x(i,item.points.length).toFixed(2)},${y(point.value).toFixed(2)}`).join(" ")}" fill="none" stroke="${colors[index]}" stroke-width="2.2"><title>${escape(item.label)} : ${number(item.points[0].value)} à ${number(item.points.at(-1).value)} CAD</title></path>`).join("");
    return `<figure class="history-chart"><svg viewBox="0 0 685 225" role="img" aria-label="Évolution historique des valeurs en CAD des allocations comparées. Les valeurs finales et périodes figurent dans les données de chaque option.">${[0,.5,1].map((fraction)=>{const value=min+span*fraction;return`<line x1="100" x2="658" y1="${y(value)}" y2="${y(value)}" stroke="#e6ecdd"/><text x="92" y="${y(value)+4}" text-anchor="end">${escape(axisValue(value))}</text>`;}).join("")}${lines}<text x="100" y="213">${escape(metadata?.start || series[0].points[0].date)}</text><text x="658" y="213" text-anchor="end">${escape(metadata?.end || series[0].points.at(-1).date)}</text></svg><figcaption>${series.map((item,index)=>`<span><i style="background:${colors[index]}"></i>${escape(item.label)}</span>`).join("")}</figcaption><p class="field-help">Historique descriptif en CAD. Aucun rendement futur n’est prédit par ces courbes.</p></figure>`;
  }
  function renderChecks(checks, heading, key) {
    const items = Array.isArray(checks) ? checks : Object.entries(object(checks)).map(([id,value]) => typeof value === "object" ? {id,...value} : {id,value});
    if (!items.length) return "";
    return `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">PORTÉE DES VÉRIFICATIONS</p><h2>${escape(heading)}</h2></div></div><div class="check-grid">${items.map((check,index) => {
      const status = check.status || (check.passed === true ? "passed" : check.passed === false ? "failed" : check.ok === true ? "passed" : check.ok === false ? "failed" : typeof check.value === "boolean" ? check.value ? "passed" : "failed" : "not_examined");
      return `<article class="check-card"><div class="check-top"><strong>${escape(check.label || check.name || title(check.id || check.dimension || `Contrôle ${index + 1}`))}</strong>${badge(status)}</div>${check.method ? `<p><strong>Mécanisme :</strong> ${escape(Array.isArray(check.method) ? `${check.method.length} contrôles détaillés conservés dans les données structurées.` : text(check.method))}</p>` : ""}${check.detail || check.message || check.description || check.reason || check.scope ? `<p>${escape(text(check.detail || check.message || check.description || check.reason || check.scope))}</p>` : ""}${limitBox(limitations(check.limitations,check.limits))}${check.refs ? refButtons(check.refs) : ""}</article>`;
    }).join("")}</div><div class="detail-bar"><span>Chaque contrôle conserve sa propre portée.</span>${jsonButton(key,"Voir les contrôles structurés")}</div></section>`;
  }
  function renderContext() {
    const problem = object(state.snapshot.active_problem);
    const fields = [
      ["capital_cad", money(problem.capital_cad)], ["withdrawal_cad", money(problem.withdrawal_cad)],
      ["withdrawal_months", problem.withdrawal_months != null ? `${number(problem.withdrawal_months)} mois` : "Non précisée"],
      ["horizon_years", problem.horizon_years != null ? `${number(problem.horizon_years)} ans` : "Non précisé"],
    ];
    $("context").innerHTML = `${fields.map(([key,value]) => `<div class="fact-row"><span>${escape(title(key))}</span><strong class="${problem[key] == null ? "unknown" : ""}">${escape(value)}</strong></div>`).join("")}${problem.objective ? `<p class="scope-note"><strong>Critère :</strong> ${escape(title(problem.objective))}</p>` : ""}${problem.reserve_policy ? `<p class="scope-note"><strong>Réserve :</strong> ${escape(title(problem.reserve_policy))}${problem.reserve_policy === "abstract_nominal" ? ". Hypothèse du modèle ; aucun instrument réel qualifié par ce libellé." : ""}</p>` : ""}`;
    $("revision-withdrawal").placeholder = problem.withdrawal_cad == null ? "Montant non précisé" : `Actuellement ${number(problem.withdrawal_cad)} CAD`;
  }
  function openQuestions() {
    const view = content(currentView());
    const personal = array(state.snapshot.questions).filter((item)=>item.target === "human" || item.destination === "human" || !item.type && item.field);
    const all = [...personal, ...array(view.questions || view.open_questions), ...array(state.snapshot.active_problem?.clarifications)];
    const distinct = new Map();
    for (const value of all) {
      const item = typeof value === "string" ? {question:value} : object(value);
      if (["resolved","closed","superseded","cancelled"].includes(item.status)) continue;
      const wording = item.question || item.text || item.title || JSON.stringify(item);
      // IDs belong to different provenance layers. Deduplicate wording within
      // a field, retaining distinct questions even when they share an ID.
      const key = `${item.field || ""}\n${wording.normalize("NFC").toLocaleLowerCase("fr").replace(/\s+/g," ").trim()}`;
      const previous = distinct.get(key);
      if (!previous) distinct.set(key,{...item});
      else {
        previous.blocking = previous.blocking || item.blocking;
        for (const detail of ["reason","consequence"]) {
          previous[detail] = [...new Set([previous[detail],item[detail]].filter(Boolean).map(text))].join("\n");
        }
      }
    }
    return [...distinct.values()];
  }
  function renderQuestions() {
    const questions = openQuestions();
    const groups = new Map();
    questions.forEach((question,index) => {
      const key = question.field ? `field:${question.field}` : `question:${index}`;
      if (!groups.has(key)) groups.set(key,[]);
      groups.get(key).push(question);
    });
    $("question-count").textContent = groups.size;
    $("questions").innerHTML = groups.size ? [...groups.values()].map((group) => {
      const wording = (question) => question.question || question.text || question.title || text(question);
      return `<div class="question">${group.some((question)=>question.blocking) ? '<span class="badge warning">Nécessaire pour la conclusion concernée</span>' : group.length === 1 && group[0].status ? badge(group[0].status) : ""}${group[0].field ? `<p><strong>${escape(title(group[0].field))}</strong></p>` : ""}${group.map((question)=>`<p>${escape(wording(question))}</p>${limitations(question.reason,question.consequence).map((detail)=>`<small>${escape(detail)}</small>`).join("")}`).join("")}<button class="text-button" type="button" data-answer-question="${escape(group.map(wording).join("\n"))}">Apporter une précision →</button></div>`;
    }).join("") : '<p class="empty-note">Aucune précision personnelle n’est demandée dans cet instantané. Les questions de recherche restent consultables dans « Demande & hypothèses ».</p>';
  }
  function renderMandate() {
    const problem = object(state.snapshot.active_problem);
    const keys = ["decision_type","currency","capital_cad","withdrawal_cad","withdrawal_months","horizon_years","objective","scenario_loss_limit_cad","reserve_policy","knowledge_date"];
    $("mandate").innerHTML = `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">QUALIFICATION · AGENT 0</p><h2>Le besoin formalisé</h2></div>${jsonButton("active_problem","Inspecter")}</div><p class="answer-summary">${escape(problem.question || "La demande n’a pas encore été qualifiée.")}</p><div class="structured-section"><dl class="definition-list">${keys.map((key) => `<dt>${escape(title(key))}</dt><dd>${problem[key] == null ? "Inconnu / non précisé" : escape(typeof problem[key] === "number" ? `${number(problem[key])}${key.endsWith("_cad") ? " CAD" : key === "withdrawal_months" ? " mois" : key === "horizon_years" ? " ans" : ""}` : title(problem[key]))}</dd>`).join("")}</dl></div>
      ${array(problem.holdings).length ? `<div class="structured-section"><h3>Positions initiales déclarées</h3>${renderAllocation(problem.holdings,"Positions initiales")}<p class="field-help">Les plans sont comparés à ces positions. Aucune transaction n’est exécutée.</p></div>` : ""}
      ${Object.keys(object(problem.max_asset_weights)).length ? `<div class="structured-section"><h3>Plafonds d’exposition</h3><ul class="plain-list">${Object.entries(problem.max_asset_weights).map(([asset,weight]) => `<li>${escape(asset)} : ${number(weight * 100)} %</li>`).join("")}</ul></div>` : ""}
      ${array(problem.assumptions).length ? `<div class="structured-section"><h3>Hypothèses et origine</h3>${array(problem.assumptions).map((item) => `<div class="question">${item.origin ? `<span class="badge neutral">${escape(title(item.origin))}</span>` : ""}<p>${escape(item.text || text(item))}</p></div>`).join("")}</div>` : ""}
      ${limitBox(limitations(problem.unknowns), "Inconnues conservées")}
      ${array(problem.scenarios).length ? `<div class="structured-section"><h3>Scénarios hypothétiques</h3><p class="field-help">Paramètres de calcul sans probabilité implicite. Ils ne représentent pas tous les futurs possibles.</p>${raw(problem.scenarios)}</div>` : ""}
      </section><section class="panel content-panel"><h2 class="small-heading">Déclarations et pièces de qualification</h2>${renderArtifactList(array(state.snapshot.artifacts).filter((item) => item.owner === "agent0"))}</section>${renderQuestionGraph()}`;
  }
  function renderQuestionGraph(){
    const nodes=array(state.snapshot.questions);
    if(!nodes.length)return"";
    return `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">QUESTIONS ET DÉPENDANCES</p><h2>Ce qui reste à établir</h2></div>${jsonButton("questions","Graphe structuré")}</div><p class="empty-note">Ces questions appartiennent au dossier. Une question de preuve ou de méthode ne vous demande pas de valider vous-même le calcul.</p>${nodes.map((node)=>`<div class="question"><div class="activity-title"><strong>${escape(node.question || node.title || node.id)}</strong>${badge(node.status || "open")}</div>${node.resolved_by?`<p><strong>Critère :</strong> ${escape(node.resolved_by)}</p>`:""}${array(node.dependencies).length?`<p><strong>Dépend de :</strong> ${node.dependencies.map(escape).join(" · ")}</p>`:""}${node.reopen_if?`<small><strong>Réouverture :</strong> ${escape(node.reopen_if)}</small>`:""}${refButtons(node.result_refs)}<button class="text-button" type="button" data-question-node="${escape(node.id)}">Examiner ce nœud ↗</button></div>`).join("")}</section>`;
  }
  function evidenceItems() {
    const inspected = content(currentView()).inspected_evidence;
    return array(inspected || state.snapshot.evidence).map((item) => ({...item,...content(item)}));
  }
  function renderEvidence() {
    const evidence = evidenceItems();
    $("evidence-count").textContent = evidence.length;
    $("evidence").innerHTML = `<div><p class="eyebrow">APPUI DOCUMENTAIRE · AGENT 1</p><h2 class="small-heading">Ce qui soutient le dossier — et ce qui manque</h2><p class="evidence-intro">Une source accessible n’est pas une preuve suffisante. Chaque pièce précise son passage, son niveau de lecture, sa portée et ses limites lorsqu’ils sont fournis.</p></div>
      ${evidence.length ? `<div class="source-list">${evidence.map((item,index) => {
        const source = object(item.source), sourceUrl = item.url || source.url || item.source_url || "", url = safeUrl(sourceUrl);
        const localDocument = typeof sourceUrl === "string" && sourceUrl.trim() && !/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(sourceUrl.trim());
        const unavailableLink = localDocument ? "Document local — voir provenance" : sourceUrl ? "Lien indisponible — voir provenance" : "URL non fournie";
        const reading = item.reading_level || item.reading || source.reading_level;
        const passage = item.passage || item.excerpt || item.quote || source.passage;
        const reference = refOf(item);
        return `<article class="source-card"><div class="source-topline"><span>PIÈCE ${String(index + 1).padStart(2,"0")}</span>${item.kind ? `<span class="badge neutral">${escape(title(item.kind))}</span>` : ""}${item.status ? badge(item.status) : ""}</div><h3>${escape(item.title || source.title || item.id || `Source ${index + 1}`)}</h3><p>${escape(item.publisher || source.publisher || "")}${item.known_at ? ` · Connu le ${escape(item.known_at)}` : ""}${item.as_of ? ` · Version ${escape(item.as_of)}` : ""}</p>${typeof item.selected_by_agent1 === "boolean" ? `<p><strong>Sélection :</strong> ${item.selected_by_agent1 ? "Sélectionnée pour la revue" : "Consultée, non sélectionnée"}. Appui de chaque affirmation non vérifié indépendamment.</p>` : ""}<p><strong>Lecture :</strong> ${escape(reading ? title(reading) : "Niveau non renseigné")}</p>${passage ? `<blockquote>${escape(text(passage))}</blockquote>` : '<p>Aucun passage lisible n’est fourni dans cet instantané.</p>'}${item.scope || item.claim || item.contribution ? `<p><strong>Usage :</strong> ${escape(text(item.scope || item.claim || item.contribution))}</p>` : ""}${limitBox(limitations(item.limitations, item.limits), "Limites de cette pièce")}<div class="source-actions">${url ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">Ouvrir la source ↗</a>` : `<span class="muted">${unavailableLink}</span>`}${reference ? inspectButton(reference,"Provenance complète") : `<button type="button" class="text-button" data-evidence-index="${index}">Provenance complète ↗</button>`}</div></article>`;
      }).join("")}</div>` : '<section class="empty-panel"><h2>Les preuves restent à constituer.</h2><p>Aucune pièce documentaire n’est encore fournie. Ce manque ne démontre pas l’inverse d’une affirmation.</p></section>'}
      <section class="panel content-panel"><div class="panel-heading"><h2>Toutes les pièces du dossier</h2><span class="badge neutral">${array(state.snapshot.artifacts).length}</span></div>${renderArtifactList(array(state.snapshot.artifacts))}</section>`;
  }
  function renderArtifactList(artifacts) {
    return artifacts.length ? artifacts.map((item) => `<div class="artifact-row"><div><strong>${escape(item.type || "Pièce")} · ${escape(refOf(item) || item.id)}</strong><small>${escape(roleName(item.owner))}${item.revision ? ` · Révision ${escape(item.revision)}` : ""}</small></div>${badge(item.usable === false ? "invalidated" : "committed")}${inspectButton(refOf(item),"Ouvrir")}</div>`).join("") : '<p class="empty-note" style="margin-top:12px">Aucune pièce disponible à ce stade.</p>';
  }
  function renderActivity() {
    const tasks = array(state.snapshot.tasks), attempts = array(state.snapshot.attempts), events = array(state.snapshot.events);
    $("activity").innerHTML = `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">TÂCHES ET DÉPENDANCES</p><h2>Le travail effectivement enregistré</h2></div><span class="badge neutral">${tasks.length} tâches</span></div><p class="empty-note">Ces états viennent du serveur. Ils attestent l’exécution, pas la validité scientifique d’une conclusion.</p>${tasks.length ? tasks.map((task,index) => `<div class="activity-row"><span class="activity-index">${index + 1}</span><div><div class="activity-title"><strong>${escape(roleName(task.role))}</strong>${badge(task.status)}</div><p>${escape(task.label || task.description || task.id)}</p><div class="activity-meta"><span>${escape(task.id)}</span>${task.started_at ? `<span>Début ${escape(date(task.started_at))}</span>` : ""}${task.finished_at ? `<span>Fin ${escape(date(task.finished_at))}</span>` : ""}</div>${task.error ? `<p>${escape(errorMessage(task.error))}</p>` : ""}${refButtons(task.output_refs)}${array(task.reused_refs).length ? `<p>Réutilisées : ${refButtons(task.reused_refs)}</p>` : ""}<details><summary>Entrées, dépendances et diagnostic</summary>${raw(task)}</details></div></div>`).join("") : '<p class="empty-note" style="margin-top:18px">Aucune tâche enregistrée.</p>'}</section>
      <section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">APPELS ET REÇUS</p><h2>Inférences et outils</h2></div><span class="badge neutral">${attempts.length} tentatives</span></div>${attempts.length ? attempts.map((attempt,index) => `<div class="activity-row"><span class="activity-index">${index + 1}</span><div><div class="activity-title"><strong>${escape(roleName(attempt.role))} · ${escape(attempt.tool || "Outil non précisé")}</strong>${badge(attempt.status)}</div>${attempt.detail ? `<p>${escape(typeof attempt.detail === "string" ? attempt.detail : attempt.detail.message || attempt.detail.summary || "Sortie structurée conservée dans le reçu ci-dessous.")}</p>` : ""}<div class="activity-meta">${attempt.request_id ? `<code>Request ID : ${escape(attempt.request_id)}</code>` : "<span>Aucun identifiant fournisseur fourni</span>"}${attempt.latency_ms != null ? `<span>${number(attempt.latency_ms / 1000)} s mesurées</span>` : ""}</div>${attempt.error ? `<p>${escape(errorMessage(attempt.error))}</p>` : ""}<details><summary>Consommation, références et diagnostic</summary>${raw(attempt)}</details></div></div>`).join("") : '<p class="empty-note">Aucun reçu n’est fourni. Une carte de rôle ne constitue pas une preuve d’inférence.</p>'}</section>
      <section class="panel content-panel"><div class="panel-heading"><h2>Événements du dossier</h2><span class="badge neutral">${events.length}</span></div>${events.length ? events.slice().reverse().map((event) => `<div class="activity-row"><span class="activity-index" aria-hidden="true">·</span><div><div class="activity-title"><strong>${escape(title(event.type || event.kind || event.event_type))}</strong><span class="small-label">${escape(event.created_at ? date(event.created_at) : "")}</span></div><p>${escape(event.message || event.detail || event.reason || event.payload?.reason || event.payload?.message || event.payload?.prompt || event.payload?.view_ref || event.id || "")}</p><details><summary>Événement structuré</summary>${raw(event)}</details></div></div>`).join("") : '<p class="empty-note">Aucun événement disponible.</p>'}</section>`;
  }
  function renderHistory() {
    const comparison = state.snapshot.comparison, revisions = array(state.snapshot.revisions);
    let html = "";
    if (comparison) {
      const before = content(comparison.before), after = content(comparison.after);
      html += `<section class="panel content-panel comparison-banner"><div class="section-heading"><div><p class="eyebrow">AVANT / APRÈS</p><h2>Ce que la révision change</h2></div></div><p>Champs modifiés : ${array(comparison.changed_fields).length ? comparison.changed_fields.map((key) => escape(title(typeof key === "string" ? key : key.field || text(key)))).join(" · ") : "détail non fourni"}.</p><div class="delta-lists"><div><h3>Résultats à réexaminer</h3><div class="ref-list">${array(comparison.invalidated).map((ref) => `<span class="ref-chip">${escape(text(ref))}</span>`).join("") || '<span class="field-help">Aucun signalé</span>'}</div></div><div><h3>Pièces réutilisées</h3><div class="ref-list">${array(comparison.reused).map((ref) => `<span class="ref-chip">${escape(text(ref))}</span>`).join("") || '<span class="field-help">Aucune signalée</span>'}</div></div></div></section>`;
      const oldOptions = array(before.options), newOptions = array(after.options);
      html += `<section class="panel content-panel"><h2 class="small-heading">Comparaison des analyses versionnées</h2><p class="field-help">L’ancienne analyse reste rattachée à son ancien besoin. Le tableau n’implique aucune transaction entre les deux plans.</p>${oldOptions.length || newOptions.length ? renderComparisonTable(before,after) : '<p class="empty-note" style="margin-top:15px">Le nouveau calcul n’est pas encore disponible pour la comparaison.</p>'}<details class="metric-details"><summary>Avant / après : données et références complètes</summary>${raw(comparison)}</details></section>`;
    }
    html += `<section class="panel content-panel"><div class="section-heading"><div><p class="eyebrow">HISTORIQUE CONSERVÉ</p><h2>Les versions du dossier</h2></div>${jsonButton("snapshot","Instantané complet")}</div><p class="empty-note">Une vue préparée, un affichage et un choix explicite sont des événements différents. L’export conserve le dossier et sa portée actuelle.</p>${revisions.length ? revisions.slice().reverse().map((revision) => `<div class="activity-row"><span class="activity-index">${escape(revision.revision ?? revision.number ?? "·")}</span><div><div class="activity-title"><strong>${escape(revision.reason || revision.message || revision.summary || revision.payload?.reason || revision.payload?.message || revision.payload?.prompt || title(revision.kind) || `Révision ${revision.revision ?? revision.number ?? ""}`)}</strong></div><div class="activity-meta">${revision.created_at ? `<span>${escape(date(revision.created_at))}</span>` : ""}${revision.role || revision.producer_role || revision.actor ? `<span>${escape(roleName(revision.role || revision.producer_role || revision.actor))}</span>` : ""}</div><details><summary>Changement, auteur et références</summary>${raw(revision)}</details></div></div>`).join("") : '<p class="empty-note" style="margin-top:18px">Aucune liste de révisions n’est encore fournie.</p>'}</section>`;
    $("history").innerHTML = html;
  }
  function renderComparisonTable(before,after) {
    const choose=(options)=>array(options).find((item)=>item.id==="minimum_turnover") || array(options).find((item)=>item.id!=="baseline");
    const a = choose(before.options), b = choose(after.options);
    const keys = [...new Set([...Object.keys(object(a?.metrics)),...Object.keys(object(b?.metrics))])].filter((key) => {
      const va=metricValue(a?.metrics?.[key],key), vb=metricValue(b?.metrics?.[key],key);
      return typeof va.value === "number" || typeof vb.value === "number";
    });
    const weights = [...new Set([...weightEntries(a?.weights).map(([asset])=>asset),...weightEntries(b?.weights).map(([asset])=>asset)])];
    const wa=Object.fromEntries(weightEntries(a?.weights)), wb=Object.fromEntries(weightEntries(b?.weights));
    const newLabel=b?.label || (after.status==="infeasible"?"aucune option admissible dans le modèle":after.status==="error"?"calcul en erreur":after.status?"aucune nouvelle option disponible":"nouvelle analyse en attente");
    const nonUnique=before.optimal_face?.non_unique_witness_found || after.optimal_face?.non_unique_witness_found;
    return `<p class="field-help">Options comparées : ${escape(a?.label || "ancienne solution indisponible")} → ${escape(newLabel)}. Toutes les options restent dans les pièces.</p>${after.status?`<p style="margin-top:10px">${badge(after.status)}</p>`:""}${!b?'<p class="field-help">L’allocation initiale reste une référence ; elle n’est pas présentée comme une nouvelle solution.</p>':""}${nonUnique?'<p class="field-help">Plusieurs optima existent. Ce tableau compare des témoins de solution ; leurs écarts de poids ne sont pas tous imposés par la nouvelle contrainte.</p>':""}<div class="table-wrap" style="margin-top:15px"><table class="data-table"><thead><tr><th>Valeur</th><th class="numeric">Ancienne portée</th><th class="numeric">Nouvelle portée</th></tr></thead><tbody>${keys.map((key) => { const va=metricValue(a?.metrics?.[key],key),vb=metricValue(b?.metrics?.[key],key); return `<tr><td>${escape(va.label || vb.label)}</td><td class="numeric">${number(va.value)} ${escape(va.unit)}</td><td class="numeric">${number(vb.value)} ${escape(vb.unit)}</td></tr>`; }).join("")}${weights.map((asset) => `<tr><td>${escape(title(asset))}</td><td class="numeric">${wa[asset] == null ? "—" : `${number(wa[asset] * 100)} %`}</td><td class="numeric">${wb[asset] == null ? "—" : `${number(wb[asset] * 100)} %`}</td></tr>`).join("")}</tbody></table></div>`;
  }
  function renderRoute() {
    const route = state.snapshot.route;
    const label = typeof route === "string" ? route : route?.provider || route?.mode || "";
    $("route-note").innerHTML = `<strong>Route déclarée par le serveur</strong>${escape(label || "Non fournie")}${route && typeof route === "object" ? `<br>${escape([route.model_id || route.model, route.region || route.entry_region, route.profile].filter(Boolean).join(" · "))}` : ""}<br>${jsonButton("route","Inspecter la route")}`;
  }
  function setTab(tab, focus = false) {
    if (!["overview","mandate","evidence","activity","history"].includes(tab)) return;
    state.tab = tab;
    document.querySelectorAll(".tab").forEach((button) => { const active = button.dataset.tab === tab; button.classList.toggle("active",active); button.setAttribute("aria-selected",String(active)); button.tabIndex=active?0:-1; if (active && focus) button.focus(); });
    document.querySelectorAll(".tab-panel").forEach((panel) => { panel.hidden = panel.id !== `tab-${tab}`; });
    markDisplayed();
  }
  async function markDisplayed() {
    const wrapper = currentView(), ref = refOf(wrapper);
    if (!ref || !state.snapshot || state.tab !== "overview" || document.hidden || $("dossier-view").hidden) return;
    const id = state.snapshot.id, key = `${id}:${ref}`;
    if (state.displayKeys.has(key)) return;
    state.displayKeys.add(key);
    await new Promise((resolve)=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    if(document.hidden || state.tab!=="overview" || state.snapshot?.id!==id || refOf(currentView())!==ref){state.displayKeys.delete(key);return;}
    try { await api(`/api/dossiers/${encodeURIComponent(id)}/display`, {method:"POST",body:JSON.stringify({view_ref:ref})}); }
    catch (error) { state.displayKeys.delete(key); if (state.snapshot?.id === id) showError(`La réponse est visible, mais son événement d’affichage n’a pas pu être enregistré : ${error.message}`); }
  }
  function inspector(titleText, value) {
    $("inspector-title").textContent = titleText;
    $("inspector-body").innerHTML = raw(value);
    if (!$("inspector").open) $("inspector").showModal();
  }
  async function inspectRef(ref) {
    const artifacts = array(state.snapshot?.artifacts);
    const local = artifacts.find((item) => refOf(item) === ref || item.id === ref);
    if (local) { inspector(ref, local); return; }
    const evidence=evidenceItems().find((item)=>refOf(item)===ref || item.id===ref);
    if(evidence){inspector(ref,evidence);return;}
    const wrappers = [state.snapshot?.current_view,state.snapshot?.current_analysis].filter(Boolean);
    const wrapper = wrappers.find((item) => refOf(item) === ref);
    if (wrapper) { inspector(ref, wrapper); return; }
    const match = String(ref).match(/^(.*)@(\d+)$/);
    if (!match || !state.snapshot) { inspector("Référence non retrouvée dans cet instantané", {reference:ref, note:"La pièce n’est pas disponible dans l’instantané reçu. Cette absence ne vaut pas vérification de la référence."}); return; }
    try { const result=await api(`/api/dossiers/${encodeURIComponent(state.snapshot.id)}/artifacts/${encodeURIComponent(match[1])}/${match[2]}`); inspector(ref,result); }
    catch (error) { inspector("Pièce indisponible",{reference:ref,error:error.message}); }
  }
  function inspectKey(key) {
    const view = content(currentView()), analysis = content(currentAnalysis());
    const map = {snapshot:state.snapshot, active_problem:state.snapshot?.active_problem, route:state.snapshot?.route, questions:state.snapshot?.questions, "view-checks":view.controls || view.verification, "analysis-checks":analysis.checks};
    inspector(key === "snapshot" ? "Instantané du dossier actif" : title(key), map[key] ?? null);
  }
  document.addEventListener("click",(event) => {
    const button=event.target.closest("button");
    if (!button) return;
    if (button.dataset.example) openExample(button.dataset.example);
    else if (button.dataset.openDossier) openDossier(button.dataset.openDossier);
    else if (button.dataset.tab) setTab(button.dataset.tab);
    else if (button.dataset.inspectRef) inspectRef(button.dataset.inspectRef);
    else if (button.dataset.inspectKey) inspectKey(button.dataset.inspectKey);
    else if (button.dataset.resultPointer) {
      const pointer=button.dataset.resultPointer;
      const value=pointer.split("/").slice(1).map((part)=>part.replace(/~1/g,"/").replace(/~0/g,"~")).reduce((item,key)=>item?.[key],content(currentAnalysis()));
      inspector("Valeur liée au calcul",{analysis_ref:refOf(currentAnalysis()),pointer,value:value??null});
    }
    else if(button.dataset.questionNode)inspector("Question et dépendances",array(state.snapshot?.questions).find((node)=>node.id===button.dataset.questionNode));
    else if (Object.hasOwn(button.dataset,"evidenceIndex")) inspector("Pièce documentaire", evidenceItems()[Number(button.dataset.evidenceIndex)]);
    else if (button.dataset.role) {
      const role=button.dataset.role;
      inspector(roleName(role), {tasks:array(state.snapshot?.tasks).filter((item)=>item.role===role), attempts:array(state.snapshot?.attempts).filter((item)=>item.role===role), artifacts:array(state.snapshot?.artifacts).filter((item)=>item.owner===role)});
    } else if (Object.hasOwn(button.dataset,"resume")) resume();
    else if (Object.hasOwn(button.dataset,"answerQuestion")) {
      $("revision-message").value=`Concernant « ${button.dataset.answerQuestion} » : `;
      $("revision-message").focus(); $("revision-message").scrollIntoView({behavior:"smooth",block:"center"});
    }
  });
  $("new-dossier").addEventListener("click",newDossier);
  $("create-form").addEventListener("submit",createDossier);
  $("export").addEventListener("click",(event)=>{if(state.pending)event.preventDefault();});
  $("revise-form").addEventListener("submit",reviseDossier);
  $("refresh").addEventListener("click",async () => { showError(""); if (state.snapshot) await poll(); try { await loadLibrary(); } catch(error) { showError(error.message); } });
  $("inspector-close").addEventListener("click",()=>$("inspector").close());
  $("inspector").addEventListener("click",(event)=>{if(event.target===$("inspector")){const rect=$("inspector").getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)$("inspector").close();}});
  $("facts-json").addEventListener("change",() => { try { const facts=parseObject($("facts-json").value,"Entrées"); document.querySelectorAll("[data-fact]").forEach((input)=>{input.value=facts[input.dataset.fact]??"";}); } catch {} });
  document.querySelectorAll("[data-fact]").forEach((input)=>input.addEventListener("change",()=>{try{const facts=parseObject($("facts-json").value,"Entrées");if(input.value==="")delete facts[input.dataset.fact];else facts[input.dataset.fact]=Number(input.value);$("facts-json").value=JSON.stringify(facts,null,2);}catch{}}));
  document.querySelector(".tabs").addEventListener("keydown",(event)=>{if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;const tabs=[...document.querySelectorAll(".tab")];const index=tabs.indexOf(document.activeElement);if(index<0)return;event.preventDefault();const target=event.key==="Home"?0:event.key==="End"?tabs.length-1:(index+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length;setTab(tabs[target].dataset.tab,true);});
  document.addEventListener("visibilitychange",()=>{if(!document.hidden){markDisplayed();schedulePoll(100);}});
  async function init() {
    document.querySelector(".tabs").setAttribute("role","tablist");
    document.querySelectorAll(".tab").forEach((button)=>{
      button.id=`tab-button-${button.dataset.tab}`;button.setAttribute("role","tab");button.setAttribute("aria-controls",`tab-${button.dataset.tab}`);
      const panel=$(`tab-${button.dataset.tab}`);panel.setAttribute("role","tabpanel");panel.setAttribute("aria-labelledby",button.id);
    });
    setTab(state.tab);
    const results=await Promise.allSettled([api("/api/dossiers/examples"),loadLibrary()]);
    if(results[0].status==="fulfilled"){state.examples=array(results[0].value.examples);renderExamples();}
    else{$("examples").innerHTML='<p class="muted">Les exemples sont indisponibles pour le moment.</p>';showError(results[0].reason.message);}
    if(results[1].status==="rejected"){$("dossier-list").innerHTML='<p class="sidebar-empty">Bibliothèque indisponible. Utilisez Actualiser pour réessayer.</p>';showError(results[1].reason.message);}
    const id=new URLSearchParams(location.search).get("dossier");
    if(id)await openDossier(id);
  }
  init();
})();
