

// Escucha el mensaje desde el content‑script y abre la pestaña
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "abrir_dashboard") {
    chrome.tabs.create({ url: "http://127.0.0.1:8501" });   // ⇦ cambia aquí si lo necesitas
  }
});

