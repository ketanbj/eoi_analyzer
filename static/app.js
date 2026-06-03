(function () {
  function createIcons() {
    if (window.lucide) {
      window.lucide.createIcons({
        attrs: {
          "stroke-width": 1.8,
        },
      });
    }
  }

  function formatBytes(bytes) {
    if (!bytes) {
      return "0 KB";
    }

    var units = ["B", "KB", "MB", "GB"];
    var size = bytes;
    var unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size = size / 1024;
      unitIndex += 1;
    }

    var precision = unitIndex === 0 ? 0 : 1;
    return size.toFixed(precision) + " " + units[unitIndex];
  }

  function renderFiles(input, list) {
    var files = Array.prototype.slice.call(input.files || []);
    list.replaceChildren();

    if (!files.length) {
      var empty = document.createElement("span");
      empty.textContent = "No files selected";
      list.appendChild(empty);
      return;
    }

    files.forEach(function (file) {
      var row = document.createElement("div");
      row.className = "file-row";

      var name = document.createElement("span");
      name.className = "file-name";
      name.textContent = file.name;

      var size = document.createElement("span");
      size.className = "file-size";
      size.textContent = formatBytes(file.size);

      row.append(name, size);
      list.appendChild(row);
    });
  }

  function initUploadForm() {
    var form = document.querySelector("[data-upload-form]");
    if (!form) {
      return;
    }

    var input = form.querySelector("[data-file-input]");
    var list = form.querySelector("[data-file-list]");
    var dropzone = form.querySelector("[data-dropzone]");
    var loading = document.querySelector("[data-loading]");
    var submitButton = form.querySelector("[data-submit-button]");
    var submitText = submitButton ? submitButton.querySelector("span:last-child") : null;

    if (!input || !list || !dropzone) {
      return;
    }

    input.addEventListener("change", function () {
      renderFiles(input, list);
    });

    ["dragenter", "dragover"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropzone.classList.add("drag-active");
      });
    });

    ["dragleave", "drop"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropzone.classList.remove("drag-active");
      });
    });

    dropzone.addEventListener("drop", function (event) {
      if (event.dataTransfer && event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        renderFiles(input, list);
      }
    });

    form.addEventListener("submit", function () {
      if (loading) {
        loading.hidden = false;
      }
      if (submitButton) {
        submitButton.disabled = true;
      }
      if (submitText) {
        submitText.textContent = "Analyzing";
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    createIcons();
    initUploadForm();
  });
})();
