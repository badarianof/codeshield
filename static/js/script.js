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
}
