const CACHE_NAME = 'smartpark-v2';
const STATIC_ASSETS = [
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/icon-192.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.log('Cache addAll error:', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Skip caching for admin, login, logout, and booking operations
    if (url.pathname.includes('/admin/') || 
        url.pathname.includes('/login/') || 
        url.pathname.includes('/logout/') ||
        url.pathname.includes('/book/') ||
        url.pathname.includes('/cancel/') ||
        url.pathname.includes('/extend-booking/')) {
        return;
    }
    
    // Cache static assets only
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then(cache => {
                return cache.match(event.request).then(cached => {
                    return cached || fetch(event.request).then(response => {
                        cache.put(event.request, response.clone());
                        return response;
                    }).catch(err => {
                        console.log('Fetch error:', err);
                        return cached || new Response('Offline');
                    });
                });
            }).catch(err => {
                console.log('Cache error:', err);
                return fetch(event.request);
            })
        );
        return;
    }
    
    // Always fetch HTML pages fresh from network
    event.respondWith(
        fetch(event.request).catch(err => {
            console.log('Network fetch error:', err);
            return new Response('Network error', { status: 503 });
        })
    );
});