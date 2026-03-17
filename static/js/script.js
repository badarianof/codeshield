function openFile() {
  const fileInput = document.getElementById("fileInput");
  if (fileInput) {
    fileInput.click();
  }
}

const fileInput = document.getElementById("fileInput");

if (fileInput) {
  fileInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      document.getElementById("fileName").value = file.name;
    }
  });

  const runBtn = document.querySelector(".btn-run");

  if (runBtn) {
    runBtn.addEventListener("click", async function () {
      const file = fileInput.files[0];

      if (!file) {
        alert("Please select a .py file first.");
        return;
      }

      const source = await file.text();

      const response = await fetch("/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: source, filename: file.name }),
      });

      const data = await response.json();

      showResults(data);
    });
  }
}

function showResults(data) {
  let history = JSON.parse(sessionStorage.getItem("scanHistory")) || [];

  const avgTDI =
    data.functions.reduce((sum, f) => sum + f.complexity, 0) /
    data.functions.length;

  const scan = {
    date: new Date().toLocaleString(),
    filename: data.filename,
    filesScanned: 1,
    avgTDI: avgTDI.toFixed(1),
    results: data,
  };

  history = history.filter((h) => h.filename !== scan.filename);

  history.unshift(scan);
  sessionStorage.setItem("scanHistory", JSON.stringify(history));

  sessionStorage.setItem("scanResults", JSON.stringify(data));

  window.location.href = "/scanResult";
}

const container = document.getElementById("historyContainer");

if (container) {
  const history = JSON.parse(sessionStorage.getItem("scanHistory")) || [];

  history.forEach((scan) => {
    const tdi = scan.avgTDI || scan.avgComplexity || 0;

    let risk = "LOW";

    if (tdi > 40) risk = "HIGH";
    else if (tdi > 20) risk = "MED";

    const card = document.createElement("div");
    card.className = "scan-card";

    card.innerHTML = `
  <div class="scan-header">
    ${scan.date} | ${scan.filename}
  </div>

  <div class="scan-body">

    <div class="metric">
      <div class="metric-number">${scan.filesScanned}</div>
      <div class="metric-label">Files Scanned</div>
    </div>

    <div class="metric">
      <div class="metric-number">${tdi}</div>
      <div class="metric-label">Avg TDI</div>
    </div>

    <div class="risk ${risk.toLowerCase()}">
      ${risk}
    </div>

    <button class="view-btn">
      View Results
    </button>

  </div>
`;

    container.appendChild(card);
  });
}
