(function () {
  // Evita duplicar el botón si Gmail recarga internamente su UI
  if (document.getElementById("mi-boton-gmail")) return;

  const btn = document.createElement("button");
  btn.id = "mi-boton-gmail";
  btn.textContent = "Asistente";

  // Estilos
  Object.assign(btn.style, {
    backgroundColor: "#34a853",
    position: "fixed",
    bottom: "15px",
    right: "15px",
    padding: "10px 14px",
    color: "white",
    border: "none",
    borderRadius: "8px",
    zIndex: "9999",
    cursor: "pointer",
    boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
    fontWeight: "bold",
    fontFamily: "Roboto, sans-serif",
  });

  // Al hacer clic, envía mensaje al service worker
  btn.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "abrir_dashboard" });
  });

  document.body.appendChild(btn);
})();

