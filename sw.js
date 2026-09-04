// 발리 여행 가이드 Service Worker (v16)
// 전략: HTML은 network-first, 나머지는 cache-first
const CACHE_NAME = 'bali-guide-v16';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

// 설치: 핵심 파일 캐싱
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// 활성화: 옛 캐시 정리
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// fetch: HTML은 network-first, 나머지는 cache-first
self.addEventListener('fetch', (e) => {
  const req = e.request;

  // HTML 요청 (navigate 또는 .html) → 네트워크 우선
  const isHtml = req.mode === 'navigate' ||
                 req.destination === 'document' ||
                 req.url.endsWith('.html');

  if (isHtml) {
    e.respondWith(
      fetch(req).then((res) => {
        // 성공하면 캐시 갱신 (오프라인 대비)
        if (req.url.startsWith(self.location.origin)) {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
        }
        return res;
      }).catch(() => caches.match(req))  // 오프라인 시만 캐시 폴백
    );
    return;
  }

  // 이미지·CSS·JS·JSON → 캐시 우선 (오프라인 성능 유지)
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        if (req.url.startsWith(self.location.origin)) {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
        }
        return res;
      }).catch(() => cached);
    })
  );
});
