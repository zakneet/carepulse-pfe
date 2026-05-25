/*
  pwa-install.js
  - Handles the beforeinstallprompt event and toggles the install button.
  - Exposes a simple API to show/hide the install prompt.
*/
let deferredPrompt = null;
const installBtn = document.getElementById('pwa-install-btn');

console.log('[PWA] install helper loaded');

window.addEventListener('appinstalled', () => {
  console.log('[PWA] appinstalled fired');
  deferredPrompt = null;
  if (installBtn) {
    installBtn.style.display = 'none';
  }
});

window.addEventListener('manifesterror', (event) => {
  console.error('[PWA] manifesterror event:', event);
});

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  deferredPrompt = e;
  console.log('[PWA] beforeinstallprompt received, showing install button');
  if (installBtn) {
    installBtn.style.display = 'inline-flex';
  }
});

if (installBtn) {
  installBtn.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    console.log('[PWA] install button clicked, opening prompt');
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;
    deferredPrompt = null;
    installBtn.style.display = 'none';
    console.log('PWA install result:', choice.outcome);
  });
}

// Optional: expose to window for debugging
window.__pwa = { getDeferredPrompt: () => deferredPrompt };
