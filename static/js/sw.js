/*
  Service Worker (sw.js)
  - Cache important static assets during install (core shell)
  - Serve assets with cache-first strategy
  - Use network-first for API calls (requests to /api or /weather)
  - Provide offline fallback page for navigation requests

  NOTE: Keep this file small and self-contained. Update CACHE_VERSION when changing assets.
*/
const CACHE_VERSION = 'v1::opticlinic';
const CORE_ASSETS = [
  '/',
  '/offline',
  '/static/manifest.json',
  '/static/css/pwa.css',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  console.log('[SW] install', CACHE_VERSION);
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      // Cache the shell assets
      return cache.addAll(CORE_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] activate', CACHE_VERSION);
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

// Helper to determine if request is API-like
function isApiRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api') || url.pathname.startsWith('/weather');
}

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Network-first for API calls (keep data fresh)
  if (isApiRequest(req)) {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          // optionally update the cache for API responses
          return resp;
        })
        .catch((err) => {
          console.warn('[SW] API request failed, serving offline fallback:', req.url, err);
          return caches.match('/offline');
        })
    );
    return;
  }

  // For navigation requests, try network first, fallback to cache, then to offline page
  if (req.mode === 'navigate' || (req.method === 'GET' && req.headers.get('accept')?.includes('text/html'))) {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          // Cache a copy of the page for offline usage
          const copy = resp.clone();
          caches.open(CACHE_VERSION).then(c => c.put(req, copy));
          return resp;
        })
        .catch((err) => {
          console.warn('[SW] navigation request failed, using cache/offline:', req.url, err);
          return caches.match(req).then(r => r || caches.match('/offline'));
        })
    );
    return;
  }

  // Cache-first for static assets (CSS/JS/images)
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((resp) => {
        // Only cache successful GET requests
        if (req.method === 'GET' && resp && resp.status === 200 && resp.type !== 'opaque') {
          const cloned = resp.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(req, cloned));
        }
        return resp;
      }).catch(() => {
        console.warn('[SW] asset request failed, trying fallback:', req.url);
        // If request is for an image, return a tiny SVG placeholder from cache if present
        if (req.destination === 'image') {
          return caches.match('/static/icons/icon-192.png');
        }
        return caches.match('/offline');
      });
    })
  );
});

// Listen to messages from the page (e.g., to skipWaiting)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
