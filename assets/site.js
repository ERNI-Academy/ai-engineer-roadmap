"use strict";

(() => {
  const tabs = document.querySelector("nav.tabs");
  const activeTab = tabs?.querySelector('[aria-current="page"]');

  function revealActiveTab() {
    if (!tabs || !activeTab) return;
    const bar = tabs.getBoundingClientRect();
    const active = activeTab.getBoundingClientRect();
    // Solo mueve la barra horizontal: conserva anclas, foco y scroll vertical.
    if (active.left < bar.left) tabs.scrollLeft += active.left - bar.left;
    else if (active.right > bar.right) tabs.scrollLeft += active.right - bar.right;
  }

  revealActiveTab();
  let resizeFrame;
  window.addEventListener("resize", () => {
    window.cancelAnimationFrame(resizeFrame);
    resizeFrame = window.requestAnimationFrame(revealActiveTab);
  });
  window.addEventListener("pageshow", revealActiveTab);

  const checkboxes = [...document.querySelectorAll("[data-progress]")];
  const checklistStatus = document.getElementById("checklist-status");
  const resetButton = document.getElementById("reset-progress");
  const storageKey = "erni.ai-engineer-roadmap.v0.3.checklist";
  let storage = null;
  let persistence = "local";
  let storageReason = "";

  function currentProgress() {
    return Object.fromEntries(checkboxes.map((checkbox) => [checkbox.id, checkbox.checked]));
  }

  function isValidProgress(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    if (Object.keys(value).length !== checkboxes.length) return false;
    return checkboxes.every((checkbox) =>
      Object.hasOwn(value, checkbox.id) && typeof value[checkbox.id] === "boolean"
    );
  }

  function showProgress() {
    const marked = checkboxes.filter((checkbox) => checkbox.checked).length;
    const saved = persistence === "local"
      ? "Guardado local en este navegador; no se sincroniza entre dispositivos."
      : `${storageReason} Las casillas funcionan solo en esta visita; no se garantiza su conservación al recargar.`;
    checklistStatus.textContent = `${marked} de ${checkboxes.length} casillas marcadas. ${saved} No constituye aprobación del mentor.`;
  }

  function saveProgress() {
    if (persistence === "local") {
      try {
        storage.setItem(storageKey, JSON.stringify(currentProgress()));
      } catch {
        persistence = "memory";
        storageReason = "No se ha podido guardar en este navegador.";
      }
    }
    showProgress();
  }

  if (checkboxes.length && checklistStatus && resetButton) {
    // El JSON local también es entrada no fiable. No se restaura texto ni claves ajenas.
    for (const checkbox of checkboxes) checkbox.checked = false;
    try {
      storage = window.localStorage;
      const stored = storage.getItem(storageKey);
      if (stored !== null) {
        const progress = JSON.parse(stored);
        if (!isValidProgress(progress)) throw new Error("Formato de progreso incompatible");
        for (const checkbox of checkboxes) checkbox.checked = progress[checkbox.id];
      }
    } catch {
      persistence = "memory";
      storageReason = "El guardado local no está disponible o sus datos no son válidos.";
    }
    // Verificar la escritura permite anunciar guardado solo cuando ha funcionado.
    saveProgress();
    for (const checkbox of checkboxes) checkbox.addEventListener("change", saveProgress);
    resetButton.hidden = false;
    resetButton.addEventListener("click", () => {
      if (!window.confirm("¿Reiniciar las 15 casillas de este navegador? Esto no modifica ninguna evaluación del mentor.")) return;
      for (const checkbox of checkboxes) checkbox.checked = false;
      // El reinicio explícito permite reparar también un JSON local incompatible.
      try {
        storage = window.localStorage;
        storage.setItem(storageKey, JSON.stringify(currentProgress()));
        persistence = "local";
        storageReason = "";
      } catch {
        persistence = "memory";
        storageReason = "No se ha podido reiniciar el guardado local; puede reaparecer el estado anterior al recargar.";
      }
      showProgress();
    });
  }

  const copyButton = document.getElementById("copy-template");
  const weeklyTemplate = document.getElementById("weekly-template");
  const copyStatus = document.getElementById("copy-status");
  if (copyButton && weeklyTemplate && copyStatus) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(weeklyTemplate.textContent);
        copyStatus.textContent = "Plantilla copiada. Complétala en el entorno de formación autorizado.";
      } catch {
        copyStatus.textContent = "No se ha podido copiar. Selecciona el texto de la plantilla o usa «Descargar plantilla .md».";
      }
    });
  }
})();
