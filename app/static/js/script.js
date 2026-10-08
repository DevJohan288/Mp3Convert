(function () {
  const searchForm = document.getElementById("search-form");
  const urlInput = document.getElementById("url-input");
  const searchBtn = document.getElementById("search-btn");
  const errorMsg = document.getElementById("error-msg");

  const trackCard = document.getElementById("track-card");
  const trackThumb = document.getElementById("track-thumb");
  const trackTitle = document.getElementById("track-title");
  const trackUploader = document.getElementById("track-uploader");
  const trackDuration = document.getElementById("track-duration");

  const formatToggle = document.getElementById("format-toggle");
  const segments = formatToggle.querySelectorAll(".segment");
  const segmentHighlight = formatToggle.querySelector(".segment-highlight");
  const qualitySelect = document.getElementById("quality-select");
  const downloadBtn = document.getElementById("download-btn");

  const QUALITY_OPTIONS = {
    mp3: [
      { value: "128", label: "128 kbps" },
      { value: "192", label: "192 kbps" },
      { value: "320", label: "320 kbps" },
    ],
    mp4: [
      { value: "360", label: "360p" },
      { value: "480", label: "480p" },
      { value: "720", label: "720p" },
      { value: "1080", label: "1080p" },
    ],
  };

  let currentFormat = "mp3";

  buildWaveform();
  populateQualityOptions();

  searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await handleSearch();
  });

  segments.forEach((seg) => {
    seg.addEventListener("click", () => {
      if (seg.dataset.format === currentFormat) return;
      currentFormat = seg.dataset.format;
      segments.forEach((s) => s.classList.toggle("active", s === seg));
      segmentHighlight.classList.toggle("shift", currentFormat === "mp4");
      populateQualityOptions();
    });
  });

  downloadBtn.addEventListener("click", handleDownload);

  // Genera las barras del waveform y les da a cada una una animación de
  // "rebote" con duración y desfase aleatorios, para que no se vean
  // sincronizadas y parezca un visualizador de audio real.
  function buildWaveform() {
    const group = document.getElementById("waveform-bars");
    const barCount = 40;
    const width = 320 / barCount;

    for (let i = 0; i < barCount; i++) {
      const restHeight = 6 + Math.abs(Math.sin(i * 0.6)) * 22;
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");

      rect.setAttribute("x", i * width + 1);
      rect.setAttribute("y", (32 - restHeight) / 2);
      rect.setAttribute("width", Math.max(width - 2, 1));
      rect.setAttribute("height", restHeight);
      rect.setAttribute("rx", 1);

      const duration = (0.6 + Math.random() * 0.8).toFixed(2);
      const delay = (Math.random() * -1.4).toFixed(2); // negativo: arranca a mitad de ciclo
      rect.style.animationDuration = `${duration}s`;
      rect.style.animationDelay = `${delay}s`;

      group.appendChild(rect);
    }
  }

  function populateQualityOptions() {
    qualitySelect.innerHTML = "";
    QUALITY_OPTIONS[currentFormat].forEach((opt) => {
      const el = document.createElement("option");
      el.value = opt.value;
      el.textContent = opt.label;
      qualitySelect.appendChild(el);
    });
    const defaults = { mp3: "192", mp4: "720" };
    qualitySelect.value = defaults[currentFormat];
  }

  function showError(message) {
    errorMsg.textContent = message;
    errorMsg.hidden = false;
  }

  function clearError() {
    errorMsg.hidden = true;
    errorMsg.textContent = "";
  }

  function setBusy(button, busy, busyLabel, idleLabel) {
    button.disabled = busy;
    button.querySelector(".btn-label").textContent = busy ? busyLabel : idleLabel;
  }

  async function handleSearch() {
    clearError();
    const url = urlInput.value.trim();
    if (!url) return;

    trackCard.hidden = true;
    setBusy(searchBtn, true, "Buscando...", "Buscar");

    try {
      const res = await fetch("/api/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Ocurrió un error inesperado.");
        return;
      }

      trackThumb.src = data.thumbnail || "";
      trackTitle.textContent = data.title;
      trackUploader.textContent = data.uploader;
      trackDuration.textContent = data.duration;
      trackCard.hidden = false;
    } catch (err) {
      showError("No se pudo conectar con el servidor.");
    } finally {
      setBusy(searchBtn, false, "Buscando...", "Buscar");
    }
  }

  // Extrae el nombre real del archivo desde el header Content-Disposition.
  // Prioriza la variante filename*=UTF-8''... (RFC 5987) porque preserva
  // acentos y ñ; si no está, cae a filename="..." o filename=... sin comillas.
  function parseFilename(disposition) {
    if (!disposition) return null;

    let match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (match) {
      try {
        return decodeURIComponent(match[1].trim());
      } catch (err) {
        /* si falla el decode, seguimos con el siguiente intento */
      }
    }

    match = disposition.match(/filename="([^"]+)"/i);
    if (match) return match[1];

    match = disposition.match(/filename=([^;]+)/i);
    if (match) return match[1].trim();

    return null;
  }

  async function handleDownload() {
    clearError();
    const url = urlInput.value.trim();
    if (!url) return;

    setBusy(downloadBtn, true, "Descargando...", "Descargar");

    try {
      const res = await fetch("/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url,
          format: currentFormat,
          quality: qualitySelect.value,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        showError(data.error || "No se pudo completar la descarga.");
        return;
      }

      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition") || "";
      const filename = parseFilename(disposition) || `descarga.${currentFormat}`;

      const objectUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objectUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (err) {
      showError("No se pudo conectar con el servidor.");
    } finally {
      setBusy(downloadBtn, false, "Descargando...", "Descargar");
    }
  }
})();
