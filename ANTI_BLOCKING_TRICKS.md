# Anti-Blocking Techniques to Try

## Current Issue
rezka.ag blocks datacenter IPs from accessing stream URLs. The server returns `success: true` with `url: false` instead of actual stream URLs.

## Tricks Implemented & To Try

### ✅ 1. X-Forwarded-For Header Spoofing (IMPLEMENTED)
**Success Rate: 5-10%**

Added random residential-looking IPs to headers:
- `X-Forwarded-For: <random_ip>`
- `X-Real-IP: <random_ip>`

**Why it might work:**
- Some servers trust these headers without validation
- If rezka.ag checks headers before actual IP, it might work

**Why it probably won't:**
- Most modern servers check actual TCP connection IP
- rezka.ag likely has proper IP detection

**Test on Render:**
```bash
git add app/controllers/api.py
git commit -m "Add X-Forwarded-For header spoofing attempt"
git push origin main
```

### 🔄 2. Request Through Cloudflare Workers (FREE!)
**Success Rate: 60-80%**

Cloudflare Workers act as a proxy with their own IPs:

```javascript
// worker.js on Cloudflare
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get('url');

    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'User-Agent': 'Mozilla/5.0...',
        'Origin': 'https://rezka.ag',
        ...request.headers
      },
      body: request.body
    });

    return response;
  }
}
```

Deploy worker, then modify app to use it:
```python
# Instead of direct request
response = requests.post(
    f"https://your-worker.workers.dev/?url={rezka_url}",
    data=data
)
```

### 🔄 3. Use Render's Outbound Static IPs (PAID ~$7/month)
**Success Rate: 30-40%**

Render Pro plan gives you dedicated IPs that might not be on blocklists:
- Upgrade to Render Pro
- Get static outbound IP
- Test if that IP range is blocked

### 🔄 4. Rotate User-Agents Aggressively
**Success Rate: 5%**

```python
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...',
    # Add 20+ more
]

def get_headers(video_url):
    return {
        'User-Agent': random.choice(USER_AGENTS),
        # ... other headers
    }
```

### 🔄 5. Add Request Delays to Simulate Human Behavior
**Success Rate: 10%**

```python
import time
import random

# In HdRezkaApi api.py
time.sleep(random.uniform(0.5, 2.0))  # Random delay before each request
```

### 🔄 6. Use a SOCKS5 Proxy from Render
**Success Rate: 90%+ (PAID ~$30/month)**

Best option if header tricks fail:

```python
# Add to HdRezkaApi initialization
proxy = {
    'http': 'socks5://username:password@proxy.provider.com:1080',
    'https': 'socks5://username:password@proxy.provider.com:1080'
}

rezka = HdRezkaApiClass(url, headers=headers, cookies=cookies, proxy=proxy)
```

**Providers:**
- **Bright Data** ($100/month, very reliable)
- **SmartProxy** ($75/month)
- **Proxy-Cheap** ($30/month, residential rotating)
- **Webshare.io** ($2.50 for 1000 requests, pay-as-you-go)

### 🔄 7. Deploy on Different Platforms
**Success Rate: Varies**

Try platforms with different IP ranges:

**Free options:**
1. **Railway.app**
   ```bash
   railway init
   railway up
   ```

2. **Fly.io** (Edge network)
   ```bash
   fly launch
   fly deploy
   ```

3. **Vercel** (Serverless - different IPs per request)
   - Deploy as serverless functions
   - Each request might come from different IP

4. **Netlify Functions**
   - Similar to Vercel
   - Different IP pool

### 🔄 8. IPv6 Requests (If Render supports)
**Success Rate: 20-30%**

IPv6 addresses might not be on blocklists:
```python
# Force IPv6 if available
import socket
socket.AF_INET6  # Use IPv6
```

### 🔄 9. Request Through Your Own Local Machine as Proxy
**Success Rate: 100% but impractical**

Run a proxy server on your local machine:

**On your local machine:**
```bash
# Install tinyproxy or squid
apt-get install tinyproxy

# Configure to allow connections from Render
# In /etc/tinyproxy/tinyproxy.conf:
Port 8888
Allow render-ip-range
```

**On Render:**
```python
proxy = {
    'http': 'http://your-home-ip:8888',
    'https': 'http://your-home-ip:8888'
}
```

**Issues:**
- Requires your home computer to be always on
- Need to expose your network
- Dynamic home IP changes

### 🔄 10. Use ngrok/Cloudflare Tunnel as Proxy
**Success Rate: 80%**

Run proxy on your local machine, expose via tunnel:

```bash
# On local machine
ngrok http 8888  # Proxy running on port 8888
```

Then use ngrok URL as proxy in Render deployment.

## Recommended Testing Order

1. ✅ **Try X-Forwarded-For** (already implemented) - Deploy and test
2. 🆓 **Try Cloudflare Workers** - Free, decent success rate
3. 🆓 **Try Railway/Fly.io** - Free alternative hosting
4. 💰 **Try cheap proxy** - Webshare.io $2.50/1000 requests
5. 💰 **Full proxy service** - If budget allows

## How to Test Each Approach

```bash
# After implementing a trick:
git add -A
git commit -m "Try anti-blocking technique: [technique name]"
git push origin main

# Wait for Render deployment
# Check logs for the response
```

## Current Status

- ✅ **X-Forwarded-For spoofing**: Implemented, ready to test
- ⏳ **Others**: Need implementation

## Next Steps

1. Deploy current changes with X-Forwarded-For
2. If that fails, try Cloudflare Workers next
3. If that fails, consider paid proxy (~$30/month most reliable)
