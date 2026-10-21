/* nativ. service worker: the app and the map tiles stay on the phone, so it opens fast and works without signal.
   version.json is never cached (that is how updates are found). */
const DATA = 'nativ-data', APP = 'nativ-app';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('message', e => { // a new map version: forget tiles of older versions
  const dv = e.data && e.data.dv; if (!dv) return;
  e.waitUntil(caches.open(DATA).then(async c => { for (const k of await c.keys()) if (!k.url.includes('v=' + dv)) await c.delete(k); }));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  if (u.pathname.endsWith('version.json')) return;
  if (u.pathname.includes('/d/')) {
    e.respondWith(caches.open(DATA).then(async c => { const hit = await c.match(e.request); if (hit) return hit; const r = await fetch(e.request); if (r.ok) c.put(e.request, r.clone()); return r; }));
    return;
  }
  e.respondWith(fetch(e.request).then(r => { if (r.ok) { const cp = r.clone(); caches.open(APP).then(c => c.put(e.request, cp)); } return r; }).catch(() => caches.match(e.request).then(r => r || caches.match('./'))));
});
