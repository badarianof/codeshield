function openFile() {
  document.getElementById("fileInput").click();
}

document.getElementById("fileInput").addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    document.getElementById("fileName").value = file.name;
  }
});

document.querySelector(".btn-run").addEventListener("click", async function () {
  const fileInput = document.getElementById("fileInput");
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

function showResults(data) {
  let html = "<h2>Results for: " + data.filename + "</h2>";
  html += "<table border='1' cellpadding='8'>";
  html += "<tr><th>Function</th><th>Complexity</th><th>Risk</th></tr>";

  for (const fn of data.functions) {
    html += "<tr>";
    html += "<td>" + fn.function + "</td>";
    html += "<td>" + fn.complexity + "</td>";
    html += "<td>" + fn.risk + "</td>";
    html += "</tr>";
  }

  html += "</table>";

  let resultsDiv = document.getElementById("results");
  if (!resultsDiv) {
    resultsDiv = document.createElement("div");
    resultsDiv.id = "results";
    document.querySelector("main").appendChild(resultsDiv);
  }

  resultsDiv.innerHTML = html;
}
