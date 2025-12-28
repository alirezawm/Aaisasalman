/**
 * Service Worker for Asia Salman Website
 * Basic service worker for PWA functionality
 */

const CACHE_NAME = 'asiasalman-v2'; // Updated to clear old cache
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/multi-select-cart.css',
    '/static/css/points.css',
    '/static/js/main.js',
    '/static/js/multi-select-cart.js',
    '/static/js/points.js',
    '/static/js/persian-date-utils.js',
    '/static/images/logo.png'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('ServiceWorker: Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(function(error) {
                console.log('ServiceWorker: Cache failed', error);
            })
    );
    // Force the waiting service worker to become the active service worker
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('ServiceWorker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(function() {
            // Clear all caches and take control immediately
            console.log('ServiceWorker: Cache cleared, taking control');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    // Only cache GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests to avoid Tracking Prevention warnings
    const url = new URL(event.request.url);
    if (url.origin !== self.location.origin) {
        return;
    }

    // For static files, always try network first to avoid stale cache
    const isStaticFile = url.pathname.startsWith('/static/');
    
    event.respondWith(
        (isStaticFile ? 
            // For static files: Network first, then cache
            fetch(event.request).then(function(fetchResponse) {
                // If network succeeds, update cache
                if (fetchResponse && fetchResponse.status === 200) {
                    const responseToCache = fetchResponse.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseToCache);
                    });
                }
                return fetchResponse;
            }).catch(function() {
                // If network fails, try cache
                return caches.match(event.request);
            }) :
            // For other files: Cache first, then network
            caches.match(event.request).then(function(response) {
                return response || fetch(event.request).then(function(fetchResponse) {
                    // Don't cache if not a valid response
                    if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
                        return fetchResponse;
                    }

                    // Clone the response
                    const responseToCache = fetchResponse.clone();

                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });

                    return fetchResponse;
                }).catch(function(error) {
                    console.log('ServiceWorker: Fetch failed', error);
                    // Return offline page if available
                    return caches.match('/');
                });
            })
        )
    );
});

