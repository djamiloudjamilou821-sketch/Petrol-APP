const CACHE_NAME = "petroapp-v1";

const urlsToCache = [

    "/",
    "/home",
    "/lessons",
    "/quiz",
    "/formulas",
    "/converter",

    "/static/bg.jpg",
    "/static/icon-192.png",
    "/static/icon-512.png"

];


// INSTALL
self.addEventListener("install", event => {

    event.waitUntil(

        caches.open(CACHE_NAME)

        .then(cache => {

            return cache.addAll(urlsToCache);

        })

    );

});


// FETCH
self.addEventListener("fetch", event => {

    event.respondWith(

        caches.match(event.request)

        .then(response => {

            // RETURN CACHE FIRST
            if (response) {
                return response;
            }

            // OTHERWISE FETCH INTERNET
            return fetch(event.request)

            .then(networkResponse => {

                return caches.open(CACHE_NAME)

                .then(cache => {

                    cache.put(
                        event.request,
                        networkResponse.clone()
                    );

                    return networkResponse;

                });

            });

        })

    );

});