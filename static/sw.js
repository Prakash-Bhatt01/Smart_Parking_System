const CACHE_NAME = "smartpark-v3";
const STATIC_ASSETS = [
    "/static/css/style.css",
    "/static/js/main.js",
    "/static/manifest.json",
    "/static/icon-192.png",
    "/static/icon-512.png"
];

self.addEventListener("install", function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener("activate", function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                    return null;
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener("fetch", function(event) {
    if (event.request.method !== "GET") {
        return;
    }

    const url = new URL(event.request.url);

    if (
        event.request.mode === "navigate" ||
        url.pathname.startsWith("/login/") ||
        url.pathname.startsWith("/register/") ||
        url.pathname.startsWith("/book/") ||
        url.pathname.startsWith("/cancel/") ||
        url.pathname.startsWith("/extend/") ||
        url.pathname.startsWith("/my-bookings/")
    ) {
        return;
    }

    if (!url.pathname.startsWith("/static/")) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(function(cachedResponse) {
            return cachedResponse || fetch(event.request);
        })
    );
});
