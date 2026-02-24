function openFile() {
  document.getElementById("fileInput").click();
}

document.getElementById("fileInput").addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    document.getElementById("fileName").value = file.name;
  }
});
