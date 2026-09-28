const CACHE = 'vocaben-v11';
const APP_SHELL = './index.html';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'
];
const NETWORK_TIMEOUT_MS = 4000;

// Pré-cache fichier par fichier : un échec isolé (ex. polices) ne vide plus tout le cache
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => Promise.all(ASSETS.map(a => c.add(a).catch(() => {}))))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('timeout')), ms);
    promise.then(r => { clearTimeout(t); resolve(r); }, err => { clearTimeout(t); reject(err); });
  });
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Base de vocabulaire publiée : jamais servie par le service worker, pour que l'appli voie
  // toujours la dernière version (hors ligne, elle garde simplement la base de l'appareil)
  if (url.pathname.endsWith('/vocab.xlsx')) return;

  // Page de l'application (/vocaben/, /vocaben/index.html, lancement depuis l'écran d'accueil) :
  // réseau d'abord pour recevoir les mises à jour, copie en cache sinon (hors ligne ou réseau trop lent)
  if (req.mode === 'navigate' || url.pathname.endsWith('.html')) {
    e.respondWith(
      withTimeout(fetch(req), NETWORK_TIMEOUT_MS)
        .then(r => {
          if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(APP_SHELL, copy)); }
          return r;
        })
        .catch(() => caches.match(APP_SHELL))
    );
    return;
  }

  // Autres ressources (icônes, SheetJS, polices) : cache d'abord, mise en cache au premier chargement
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(r => {
      if (r.ok || r.type === 'opaque') { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return r;
    }))
  );
});
