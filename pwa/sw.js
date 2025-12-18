// Simple service worker using Cache First strategy for app shell
const CACHE_NAME = 'bible-pwa-v1';
const ASSETS = [
  'index.html',
  'app.js',
  'styles.css',
  'manifest.json',
  '../data/bible.json'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request))
  );
});
