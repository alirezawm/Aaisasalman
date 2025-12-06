/**
 * Service Worker for Asia Salman Website
 * Basic service worker for PWA functionality
 */

const CACHE_NAME = 'asiasalman-v1';
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
        })
    );
    // Take control of all pages immediately
    return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    // Only cache GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests to avoid Tracking Prevention warnings
    // Only cache resources from same origin
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }
    
    // Skip requests to external CDNs to prevent Tracking Prevention warnings
    const url = new URL(event.request.url);
    if (url.origin !== self.location.origin) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
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
    );
});

