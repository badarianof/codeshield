const fileInput = document.getElementById("fileInput");

function openFile() {
  if (fileInput) {
    fileInput.click();
  }
}

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

  const scan = {
    date: new Date().toLocaleString(),
    filename: data.filename,
    filesScanned: 1,
    tdi: data.tdi,
    risk: data.risk,
    redFlagCount: data.red_flag_count,
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
    const tdi = scan.tdi || 0;
    const risk = (scan.risk || "Low").toUpperCase();

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
      <div class="metric-number">${Number(tdi).toFixed(1)}</div>
      <div class="metric-label">Avg TDI</div>
    </div>

    <div class="metric">
      <div class="metric-number">${scan.redFlagCount || 0}</div>
      <div class="metric-label">Red Flags</div>
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

    card.querySelector(".view-btn").addEventListener("click", function () {
      sessionStorage.setItem("scanResults", JSON.stringify(scan.results));

      window.location.href = "/scanResult";
    });
  });
}
