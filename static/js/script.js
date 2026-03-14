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