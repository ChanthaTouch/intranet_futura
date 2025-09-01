<?php
return [
    'paths' => ['api/*'], // Apply CORS to API routes
    'allowed_methods' => ['*'], // Allow all HTTP methods
    'allowed_origins' => ['*'], // Allow all origins (or specify frontend domain)
    'allowed_headers' => ['*'],
    'exposed_headers' => [],
    'max_age' => 0,
    'supports_credentials' => false,
];