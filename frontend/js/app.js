/**
 * Logique principale de l'application frontend.
 * Gère la navigation, les appels API, l'affichage des graphiques et le thème.
 */

// État global de l'application
const AppState = {
  currentSection: "dashboard",
  theme: localStorage.getItem("theme") || "light",
  dataInfo: null,
  charts: {},
};

// Initialisation
document.addEventListener("DOMContentLoaded", () => {
  applyTheme(AppState.theme);
  loadDataInfo();

  // Écouteur pour le changement de thème
  document
    .getElementById("theme-toggle")
    .addEventListener("click", toggleTheme);
});

// Gestion du thème
function toggleTheme() {
  AppState.theme = AppState.theme === "light" ? "dark" : "light";
  localStorage.setItem("theme", AppState.theme);
  applyTheme(AppState.theme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-bs-theme", theme);
  const icon = document.querySelector("#theme-toggle i");
  icon.className =
    theme === "light" ? "bi bi-moon-stars-fill" : "bi bi-sun-fill";

  // Mettre à jour les graphiques si ils existent
  updateChartsTheme();
}

function updateChartsTheme() {
  const textColor = AppState.theme === "light" ? "#212121" : "#e0e0e0";
  Object.values(AppState.charts).forEach((chart) => {
    if (chart.options.plugins.legend) {
      chart.options.plugins.legend.labels.color = textColor;
    }
    if (chart.options.scales.x) {
      chart.options.scales.x.ticks.color = textColor;
      chart.options.scales.x.grid.color =
        AppState.theme === "light" ? "#dee2e6" : "#2d2d44";
    }
    if (chart.options.scales.y) {
      chart.options.scales.y.ticks.color = textColor;
      chart.options.scales.y.grid.color =
        AppState.theme === "light" ? "#dee2e6" : "#2d2d44";
    }
    chart.update();
  });
}

// Navigation
function showSection(sectionId) {
  // Cacher toutes les sections
  document
    .querySelectorAll(".content-section")
    .forEach((el) => el.classList.add("d-none"));
  // Afficher la section demandée
  document.getElementById(`section-${sectionId}`).classList.remove("d-none");

  // Mettre à jour le titre et la sidebar
  const titles = {
    dashboard: "Tableau de bord",
    data: "Gestion des Données",
    descriptive: "Analyse Statistique Descriptive",
    gaussian: "Loi de Gauss (Revenus)",
    poisson: "Loi de Poisson (Incidents)",
    reg_simple: "Régression Linéaire Simple",
    reg_multiple: "Régression Linéaire Multiple",
    reg_logistic: "Régression Logistique (Défaut)",
    export: "Exportation et Rapports",
  };
  document.getElementById("page-title").textContent = titles[sectionId];

  // Mettre à jour la classe active de la sidebar
  document
    .querySelectorAll(".list-group-item-action")
    .forEach((el) => el.classList.remove("active"));
  event.target.closest(".list-group-item-action").classList.add("active");

  AppState.currentSection = sectionId;

  // Charger les données spécifiques si nécessaire
  if (sectionId === "dashboard") loadDashboard();
}

// API Calls
async function apiCall(endpoint, method = "GET", body = null) {
  updateStatus(`Communication avec le serveur...`);
  try {
    const options = {
      method: method,
      headers: method === "POST" ? { "Content-Type": "application/json" } : {},
    };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`/api${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Erreur serveur");
    updateStatus("Opération réussie", "success");
    return data;
  } catch (error) {
    console.error(error);
    updateStatus(error.message, "error");
    alert(`Erreur : ${error.message}`);
    return null;
  }
}

// Gestion des données
async function loadDataInfo() {
  const info = await apiCall("/data_info");
  if (info && info.exists) {
    AppState.dataInfo = info;
    updateStatusBar(info);
    renderDataTable(info.preview, info.columns);
    if (AppState.currentSection === "dashboard") loadDashboard();
  }
}

async function uploadFile() {
  const fileInput = document.getElementById("file-upload");
  if (!fileInput.files.length) {
    alert("Veuillez sélectionner un fichier.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  updateStatus("Téléchargement et nettoyage en cours...");
  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);

    AppState.dataInfo = data.info;
    updateStatusBar(data.info);
    renderDataTable(data.info.preview, data.info.columns);
    alert(data.message);
  } catch (error) {
    alert("Erreur : " + error.message);
  }
}

async function generateSampleData() {
  updateStatus("Génération des données simulées...");
  const data = await apiCall("/generate", "POST");
  if (data) {
    AppState.dataInfo = data.info;
    updateStatusBar(data.info);
    renderDataTable(data.info.preview, data.info.columns);
    alert(data.message);
    loadDashboard();
  }
}

function updateStatusBar(info) {
  document.getElementById("status-file").innerHTML =
    `<i class="bi bi-file-earmark me-1"></i> credit_bancaire.csv`;
  document.getElementById("status-rows").textContent =
    `Lignes: ${info.rows} | Colonnes: ${info.cols}`;
}

function updateStatus(msg, type = "info") {
  const el = document.getElementById("status-msg");
  el.innerHTML = `<i class="bi bi-${type === "error" ? "exclamation-triangle-fill text-danger" : "info-circle-fill text-info"} me-1"></i> ${msg}`;
}

// Rendu du tableau
function renderDataTable(preview, columns) {
  const thead = document.querySelector("#data-table thead");
  const tbody = document.querySelector("#data-table tbody");

  thead.innerHTML =
    "<tr>" + columns.map((c) => `<th>${c}</th>`).join("") + "</tr>";
  tbody.innerHTML = preview
    .map((row) => {
      return (
        "<tr>" +
        columns
          .map((c) => {
            let val = row[c] !== null ? row[c] : "";
            if (c === "Defaut" && val === 1)
              return '<td><span class="badge badge-risk-high">Risque</span></td>';
            return `<td>${val}</td>`;
          })
          .join("") +
        "</tr>"
      );
    })
    .join("");
}

// Analyses
async function runAnalysis(task) {
  updateStatus(`Exécution de l'analyse : ${task}...`);
  const data = await apiCall("/analyze", "POST", { task: task });
  if (!data) return;

  if (task === "descriptive") renderDescriptive(data);
  else if (task === "gaussian") renderGaussian(data);
  else if (task === "poisson") renderPoisson(data);
  else if (task === "regression_simple") renderRegSimple(data);
  else if (task === "regression_multiple") renderRegMultiple(data);
  else if (task === "logistic") renderRegLogistic(data);
}

function renderDescriptive(data) {
  let html = '<div class="row g-3">';
  for (const [varName, stats] of Object.entries(data.stats)) {
    html += `
        <div class="col-md-4">
            <div class="card shadow-sm p-3">
                <h6 class="text-primary-custom fw-bold">${varName}</h6>
                <ul class="list-unstyled mb-0 small">
                    <li>Moyenne: ${stats.moyenne.toLocaleString("fr-FR", { maximumFractionDigits: 0 })}</li>
                    <li>Médiane: ${stats.mediane.toLocaleString("fr-FR", { maximumFractionDigits: 0 })}</li>
                    <li>Écart-type: ${stats.ecart_type.toLocaleString("fr-FR", { maximumFractionDigits: 0 })}</li>
                    <li>CV: ${(stats.cv * 100).toFixed(2)}%</li>
                </ul>
            </div>
        </div>`;
  }
  html += "</div>";

  html +=
    '<div class="alert alert-info mt-3"><strong>Interprétation :</strong><ul>' +
    data.interpretations.map((i) => `<li>${i}</li>`).join("") +
    `</ul>Valeurs aberrantes détectées (Revenu) : ${data.outliers_count}</div>`;

  document.getElementById("descriptive-results").innerHTML = html;
}

function renderGaussian(data) {
  let html = `
    <div class="row g-3 mb-3">
        <div class="col-md-4"><div class="card p-3 text-center"><h5>μ (Moyenne)</h5><h3 class="text-primary-custom">${data.mu.toLocaleString("fr-FR", { maximumFractionDigits: 0 })} FCFA</h3></div></div>
        <div class="col-md-4"><div class="card p-3 text-center"><h5>σ (Écart-type)</h5><h3 class="text-primary-custom">${data.sigma.toLocaleString("fr-FR", { maximumFractionDigits: 0 })} FCFA</h3></div></div>
        <div class="col-md-4"><div class="card p-3 text-center"><h5>P(300k < X < 800k)</h5><h3 class="text-success">${(data.probabilities.P_300k_X_800k * 100).toFixed(1)}%</h3></div></div>
    </div>
    <div class="alert alert-info"><strong>Interprétation bancaire :</strong><ul>${data.interpretation.map((i) => `<li>${i}</li>`).join("")}</ul></div>`;
  document.getElementById("gaussian-results").innerHTML = html;

  // Graphique
  renderChart("chart-gaussian", "line", {
    labels: data.curve.x.map((x) => Math.round(x / 1000) + "k"),
    datasets: [
      {
        label: "Courbe de densité normale",
        data: data.curve.y,
        borderColor: "#1a237e",
        backgroundColor: "rgba(26, 35, 126, 0.1)",
        fill: true,
        tension: 0.4,
      },
    ],
  });
}

function renderPoisson(data) {
  let html = `<div class="alert alert-info"><strong>λ (Lambda) :</strong> ${data.lambda.toFixed(2)} incidents en moyenne. ${data.interpretation}</div>`;
  html += `<table class="table table-bordered"><thead><tr><th>x</th><th>P(X=x) Réel</th><th>P(X=x) Théorique (Poisson)</th></tr></thead><tbody>`;
  for (let i = 0; i < data.comparison.x.length; i++) {
    html += `<tr><td>${data.comparison.x[i]}</td><td>${(data.comparison.reel[i] * 100).toFixed(1)}%</td><td>${(data.comparison.theorique[i] * 100).toFixed(1)}%</td></tr>`;
  }
  html += `</tbody></table>`;
  document.getElementById("poisson-results").innerHTML = html;

  renderChart("chart-poisson", "bar", {
    labels: data.comparison.x,
    datasets: [
      { label: "Réel", data: data.comparison.reel, backgroundColor: "#1565c0" },
      {
        label: "Théorique (Poisson)",
        data: data.comparison.theorique,
        backgroundColor: "#ef6c00",
      },
    ],
  });
}

function renderRegSimple(data) {
  let html = `
    <div class="card p-3 mb-3">
        <h5>Modèle : Montant_Credit = ${data.beta_0.toFixed(2)} + ${data.beta_1.toFixed(4)} * Revenu_Mensuel</h5>
        <p class="mb-0"><strong>R² =</strong> ${data.r2.toFixed(4)}</p>
    </div>
    <div class="alert alert-success"><strong>Interprétation :</strong> ${data.interpretation.join(" ")}</div>`;
  document.getElementById("reg-simple-results").innerHTML = html;
  AppState.currentSimpleModel = data;
}

function predictSimple() {
  const val = parseFloat(document.getElementById("simple-pred-input").value);
  if (AppState.currentSimpleModel) {
    const pred =
      AppState.currentSimpleModel.beta_0 +
      AppState.currentSimpleModel.beta_1 * val;
    document.getElementById("simple-pred-result").textContent =
      `Montant du crédit prédit : ${pred.toLocaleString("fr-FR", { maximumFractionDigits: 0 })} FCFA`;
  }
}

function renderRegMultiple(data) {
  let html = `<div class="card p-3 mb-3"><h5>Résultats du Modèle Multiple</h5>`;
  html += `<ul class="list-group list-group-flush">`;
  for (const [key, val] of Object.entries(data.coefficients)) {
    html += `<li class="list-group-item d-flex justify-content-between"><span>${key}</span><strong>${val.standardized.toFixed(4)}</strong></li>`;
  }
  html += `</ul>
    <div class="mt-3"><strong>R² :</strong> ${data.r2.toFixed(4)} | <strong>RMSE :</strong> ${data.rmse.toLocaleString("fr-FR", { maximumFractionDigits: 0 })}</div>
    <div class="alert alert-info mt-2">Variable la plus influente (en valeur absolue standardisée) : <strong>${data.most_influential}</strong></div>
    </div>`;
  document.getElementById("reg-multiple-results").innerHTML = html;
}

function renderRegLogistic(data) {
  let html = `<div class="row g-3 mb-3">`;
  for (const [metric, value] of Object.entries(data.metrics)) {
    html += `<div class="col-md-2"><div class="card p-2 text-center"><small>${metric.toUpperCase()}</small><h5>${value.toFixed(3)}</h5></div></div>`;
  }
  html += `</div><div class="alert alert-warning">${data.interpretation}</div>`;
  document.getElementById("reg-logistic-results").innerHTML = html;

  // Matrice de confusion
  const cm = data.confusion_matrix;
  document.getElementById("confusion-matrix-display").innerHTML = `
    <table class="table table-bordered text-center">
        <tr><td></td><th>Prédit 0</th><th>Prédit 1</th></tr>
        <tr><th>Réel 0</th><td class="bg-success text-white">${cm[0][0]}</td><td class="bg-danger text-white">${cm[0][1]}</td></tr>
        <tr><th>Réel 1</th><td class="bg-warning text-white">${cm[1][0]}</td><td class="bg-success text-white">${cm[1][1]}</td></tr>
    </table>`;

  // Courbe ROC
  renderChart("chart-roc", "line", {
    labels: data.roc_curve.fpr,
    datasets: [
      {
        label: `Courbe ROC (AUC = ${data.roc_curve.auc.toFixed(3)})`,
        data: data.roc_curve.tpr,
        borderColor: "#1a237e",
        borderWidth: 2,
        pointRadius: 0,
      },
      {
        label: "Hasard",
        data: data.roc_curve.fpr.map((x) => x),
        borderColor: "#999",
        borderDash: [5, 5],
        pointRadius: 0,
      },
    ],
  });
}

// Dashboard
async function loadDashboard() {
  if (!AppState.dataInfo) return;

  // KPI
  const info = AppState.dataInfo;
  // On fait une requête rapide pour les stats de base si pas en cache, ou on utilise des valeurs par défaut pour l'exemple
  const kpis = [
    {
      title: "Total Clients",
      value: info.rows,
      icon: "bi-people",
      color: "primary",
    },
    {
      title: "Variables",
      value: info.cols,
      icon: "bi-list-columns",
      color: "info",
    },
    {
      title: "Taux de défaut",
      value: "Calcul...",
      icon: "bi-exclamation-triangle",
      color: "danger",
    },
  ];

  document.getElementById("kpi-cards").innerHTML = kpis
    .map(
      (k) => `
        <div class="col-md-4">
            <div class="card kpi-card ${k.color} shadow-sm p-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="text-muted mb-1">${k.title}</h6>
                        <div class="kpi-value">${k.value}</div>
                    </div>
                    <i class="bi ${k.icon} fs-1 opacity-25"></i>
                </div>
            </div>
        </div>
    `,
    )
    .join("");

  // Charger les données du dashboard
  const data = await apiCall("/analyze", "POST", { task: "descriptive" });
  if (data) {
    kpis[2].value = data.default_rate.toFixed(1) + "%";
    document.getElementById("kpi-cards").innerHTML = kpis
      .map(
        (k) => `
            <div class="col-md-4">
                <div class="card kpi-card ${k.color} shadow-sm p-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="text-muted mb-1">${k.title}</h6>
                            <div class="kpi-value">${k.value}</div>
                        </div>
                        <i class="bi ${k.icon} fs-1 opacity-25"></i>
                    </div>
                </div>
            </div>
        `,
      )
      .join("");
  }

  // Graphiques Dashboard
  const chartData = await apiCall("/analyze", "POST", { task: "descriptive" }); // Simplifié pour l'exemple, utiliserait get_dashboard_charts en prod
  // Pour l'exemple, on crée des données factices basées sur les stats réelles si disponibles
  renderChart("chart-default-pie", "doughnut", {
    labels: ["Fiable (0)", "Risque (1)"],
    datasets: [
      {
        data: [100 - (data?.default_rate || 10), data?.default_rate || 10],
        backgroundColor: ["#2e7d32", "#c62828"],
      },
    ],
  });

  renderChart("chart-revenu-credit", "bar", {
    labels: ["<300k", "300-500k", "500-700k", "700k-1M", ">1M"],
    datasets: [
      {
        label: "Crédit Moyen",
        data: [150000, 350000, 600000, 900000, 1500000], // Données simplifiées pour l'exemple
        backgroundColor: "#1565c0",
      },
    ],
  });
}

// Fonction utilitaire pour Chart.js
function renderChart(canvasId, type, dataConfig) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  if (AppState.charts[canvasId]) {
    AppState.charts[canvasId].destroy();
  }

  const textColor = AppState.theme === "light" ? "#212121" : "#e0e0e0";

  AppState.charts[canvasId] = new Chart(ctx, {
    type: type,
    data: dataConfig,
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color: textColor } },
      },
      scales:
        type !== "doughnut" && type !== "pie"
          ? {
              x: {
                ticks: { color: textColor },
                grid: {
                  color: AppState.theme === "light" ? "#dee2e6" : "#2d2d44",
                },
              },
              y: {
                ticks: { color: textColor },
                grid: {
                  color: AppState.theme === "light" ? "#dee2e6" : "#2d2d44",
                },
              },
            }
          : {},
    },
  });
}

async function exportReport() {
  updateStatus("Génération du rapport Excel en cours...");
  const data = await apiCall("/export", "POST", {});
  if (data) {
    document.getElementById("export-status").innerHTML =
      `<div class="alert alert-success"><i class="bi bi-check-circle me-2"></i>${data.message} <br> Chemin : ${data.filepath}</div>`;
  }
}

async function generateAllCharts() {
  alert(
    "Cette fonction lance les analyses pour pré-charger tous les graphiques. Naviguez dans les sections pour les voir.",
  );
  await runAnalysis("descriptive");
  await runAnalysis("gaussian");
  await runAnalysis("poisson");
  await runAnalysis("regression_simple");
  await runAnalysis("regression_multiple");
  await runAnalysis("logistic");
  alert("Tous les graphiques ont été générés en arrière-plan.");
}
