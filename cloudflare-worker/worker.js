/**
 * Cloudflare Worker to proxy Supabase requests
 * This worker acts as a proxy to route Supabase API calls through Cloudflare's edge network
 */

// Configuration
const SUPABASE_URL = 'https://frpjbfuslgsirqdjdczy.supabase.co';
const ALLOWED_ORIGINS = [
  'http://localhost:3000',
  'http://localhost:8000',
  'http://127.0.0.1:3000',
  'http://127.0.0.1:8000'
];

/**
 * Handle CORS preflight requests
 */
function handleCORS(request) {
  const origin = request.headers.get('Origin');
  const headers = {
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, x-client-info, prefer',
    'Access-Control-Max-Age': '86400',
  };

  // Check if origin is allowed
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Credentials'] = 'true';
  } else if (origin) {
    headers['Access-Control-Allow-Origin'] = origin;
  }

  return new Response(null, {
    status: 204,
    headers
  });
}

/**
 * Add CORS headers to response
 */
function addCORSHeaders(response, request) {
  const origin = request.headers.get('Origin');
  const newHeaders = new Headers(response.headers);

  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    newHeaders.set('Access-Control-Allow-Origin', origin);
    newHeaders.set('Access-Control-Allow-Credentials', 'true');
  } else if (origin) {
    newHeaders.set('Access-Control-Allow-Origin', origin);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  });
}

/**
 * Main request handler
 */
async function handleRequest(request) {
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return handleCORS(request);
  }

  try {
    // Parse the request URL
    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({
        status: 'healthy',
        service: 'supabase-proxy',
        timestamp: new Date().toISOString()
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

    // Construct the Supabase URL
    const supabaseUrl = new URL(SUPABASE_URL + url.pathname + url.search);

    // Clone the headers
    const newHeaders = new Headers(request.headers);

    // Remove headers that might cause issues
    newHeaders.delete('host');
    newHeaders.delete('cf-connecting-ip');
    newHeaders.delete('cf-ray');
    newHeaders.delete('cf-visitor');

    // Forward the request to Supabase
    const supabaseRequest = new Request(supabaseUrl.toString(), {
      method: request.method,
      headers: newHeaders,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
      redirect: 'follow'
    });

    // Fetch from Supabase
    const response = await fetch(supabaseRequest);

    // Add CORS headers and return
    return addCORSHeaders(response, request);

  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Proxy error',
      message: error.message,
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

// Export for Cloudflare Workers
export default {
  async fetch(request, env, ctx) {
    return handleRequest(request);
  }
};
