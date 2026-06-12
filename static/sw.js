const CACHE_NAME = 'smartpark-v2';
const STATIC_ASSETS = [
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/icon-192.png',
    '/static/icon-512.png',
    '/static/manifest.json'
];

// INSTALL EVENT — cache static assets
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            console.log('SmartPark SW: Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        }).then(function() {
            return self.skipWaiting();
        }).catch(function(error) {
            console.log('SmartPark SW: Cache failed', error);
        })
    );
});

// ACTIVATE EVENT — clean old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(name) {
                    return name !== CACHE_NAME;
                }).map(function(name) {
                    console.log('SmartPark SW: Deleting old cache', name);
                    return caches.delete(name);
                })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

// FETCH EVENT — network first for Django pages, cache first for static assets
self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);
    
    // Skip non-GET requests completely
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Skip Django dynamic URLs — always fetch from network
    const dynamicPaths = [
        '/admin/', '/login/', '/logout/', '/register/',
        '/search/', '/lot/', '/book/', '/cancel/',
        '/extend-booking/', '/my-bookings/', '/profile/',
        '/payment/', '/booking-success/', '/check-conflict/',
        '/mark-notification-read/'
    ];
    
    const isDynamic = dynamicPaths.some(function(path) {
        return url.pathname.startsWith(path);
    });
    
    if (isDynamic) {
        event.respondWith(
            fetch(event.request).catch(function() {
                return new Response(
                    '<html><body><h2>You are offline. Please check your connection.</h2></body></html>',
                    { headers: { 'Content-Type': 'text/html' } }
                );
            })
        );
        return;
    }
    
    // For static assets — cache first, then network
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then(function(cachedResponse) {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).then(function(networkResponse) {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseToCache = networkResponse.clone();
                        caches.open(CACHE_NAME).then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });
                    }
                    return networkResponse;
                }).catch(function() {
                    return new Response('', { status: 404 });
                });
            })
        );
        return;
    }
    
    // For home page — network first with cache fallback
    if (url.pathname === '/') {
        event.respondWith(
            fetch(event.request).catch(function() {
                return caches.match(event.request);
            })
        );
        return;
    }
    
    // Default — just fetch from network
    event.respondWith(
        fetch(event.request).catch(function(error) {
            console.log('SmartPark SW: Fetch failed', error);
        })
    );
});
