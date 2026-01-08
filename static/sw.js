self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
});

self.addEventListener('fetch', (e) => {
  // Necessário para PWA ser instalável, mesmo que não faça cache agressivo
  e.respondWith(fetch(e.request));
});
