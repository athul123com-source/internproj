const fileInput = document.querySelector('input[type="file"]');
const uploadTitle = document.querySelector(".upload-title");
const uploadSubtitle = document.querySelector(".upload-subtitle");

if (fileInput && uploadTitle && uploadSubtitle) {
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    uploadTitle.textContent = file.name;
    uploadSubtitle.textContent = `${Math.round(file.size / 1024)} KB selected`;
  });
}
