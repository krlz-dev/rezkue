/**
 * Cloudflare Worker - Proxy for rezka.ag API requests
 * Deploy this at workers.cloudflare.com (FREE tier: 100,000 requests/day)
 *
 * This bypasses datacenter IP blocking by routing requests through Cloudflare's network
 */

export default {
  async fetch(request, env, ctx) {
    // Only allow POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // Get the target URL and data from the request
      const { url, data, headers: customHeaders } = await request.json();

      // Validate the target URL
      if (!url || !url.startsWith('https://rezka.ag/')) {
        return new Response('Invalid target URL', { status: 400 });
      }

      // Build form data
      const formData = new URLSearchParams();
      for (const [key, value] of Object.entries(data)) {
        formData.append(key, value);
      }

      // Make the request from Cloudflare's network
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'User-Agent': customHeaders?.['User-Agent'] || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': '*/*',
          'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
          'Accept-Encoding': 'gzip, deflate, br',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'Origin': 'https://rezka.ag',
          'Referer': customHeaders?.['Referer'] || 'https://rezka.ag',
          'X-Requested-With': 'XMLHttpRequest',
          'Cookie': 'hdmbbs=1'
        },
        body: formData.toString()
      });

      // Get response data
      const responseData = await response.json();

      // Return with CORS headers
      return new Response(JSON.stringify(responseData), {
        status: response.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }
};
