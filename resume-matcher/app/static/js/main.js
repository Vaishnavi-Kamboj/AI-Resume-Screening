const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const dropzoneIdle = document.getElementById("dropzone-idle");
const dropzoneFile = document.getElementById("dropzone-file");
const filenameDisplay = document.getElementById("filename-display");
const fileStatus = document.getElementById("file-status");
const scanBtn = document.getElementById("scan-btn");
const errorMsg = document.getElementById("error-msg");

const resultsSection = document.getElementById("results");
const statPages = document.getElementById("stat-pages");
const statWords = document.getElementById("stat-words");
const previewText = document.getElementById("preview-text");

let selectedFile = null;

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.remove("hidden");
}

function clearError() {
  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";
}

function setSelectedFile(file) {
  clearError();

  if (!file) return;

  if (file.type !== "application/pdf") {
    showError("Only PDF files are accepted.");
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    showError("File is larger than 5MB.");
    return;
  }

  selectedFile = file;
  filenameDisplay.textContent = file.name;
  fileStatus.textContent = "Ready to scan";
  dropzoneIdle.classList.add("hidden");
  dropzoneFile.classList.remove("hidden");
  scanBtn.disabled = false;
}

dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", (e) => {
  setSelectedFile(e.target.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  setSelectedFile(file);
});

scanBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  clearError();
  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning...";
  dropzone.classList.add("scanning");
  fileStatus.textContent = "Extracting text...";

  const formData = new FormData();
  formData.append("resume", selectedFile);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong.");
      fileStatus.textContent = "Ready to scan";
      return;
    }

    fileStatus.textContent = "Scan complete";
    statPages.textContent = data.num_pages;
    statWords.textContent = data.word_count;
    previewText.textContent = data.preview || "(No extractable text found — this PDF may be scanned/image-based.)";
    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showError("Upload failed. Is the server running?");
    fileStatus.textContent = "Ready to scan";
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = "Scan resume";
    dropzone.classList.remove("scanning");
  }
});

dropzone.setAttribute("tabindex", "0");
dropzone.setAttribute("role", "button");
dropzone.setAttribute("aria-label", "Upload resume PDF");
