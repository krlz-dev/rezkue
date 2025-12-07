# IP Blocking Issue - rezka.ag

## Problem

The rezka.ag API endpoints return `success: true` but `url: false` (boolean) when accessed from **datacenter/cloud hosting IPs** (like Render.com), instead of returning the actual stream URL string.

### Why This Happens

- **Works locally**: Residential IP addresses are allowed
- **Fails on Render**: Datacenter IP addresses are blocked
- **Detection method**: IP-based blocking (not headers, cookies, or user-agent)

### Error Pattern

```python
Response: {'success': True, 'url': False, 'message': '...'}
#                              ^^^^^ Should be a string, but is boolean
```

This causes:
```
AttributeError: 'bool' object has no attribute 'replace'
```

## Solutions Tried

### ✓ Custom HdRezkaApi Library (Current)
- **Status**: Implemented in `lib/HdRezkaApi/`
- **Removed**: `HdRezkaApi==7.1.0` from pip requirements
- **Benefit**: Better error handling and session management
- **Limitation**: Doesn't bypass IP blocking

### ✗ Playwright Browser Automation
- **Status**: Removed in commit `524cb05`
- **Why removed**: Too much memory (~512MB) for free tier
- **Benefit**: Could bypass some blocking by using real browser
- **Limitation**: Expensive, slow, and still might be blocked by IP

### ✓ Enhanced Headers
- **Status**: Implemented in `app/controllers/api.py:42-59`
- **Benefit**: Mimics real browser requests
- **Limitation**: Doesn't bypass IP blocking

## Recommended Solutions

### Option 1: Use Different Hosting (Free)

Try hosting providers with different IP ranges:

- **Railway.app** - Free tier with different datacenter IPs
- **Fly.io** - Edge network, might not be blocked
- **Deta Space** - Different infrastructure
- **Vercel** (for serverless endpoints)

### Option 2: Use Proxy Service (Paid)

Add residential proxy rotation:

```python
# Add to requirements.txt
requests[socks]==2.31.0

# In HdRezkaApi.__init__
self.proxy = {
    'http': 'socks5://user:pass@proxy.provider.com:1080',
    'https': 'socks5://user:pass@proxy.provider.com:1080'
}
```

**Proxy providers**:
- ScraperAPI (~$29/month)
- Bright Data (~$500/month)
- Oxylabs (~$100/month)
- SmartProxy (~$75/month)

### Option 3: Hybrid Approach

- Keep the app on Render for the UI/frontend
- Run API requests through a separate service on a different host
- Use webhooks/queues to communicate

### Option 4: Accept Limitation

Document that streaming only works when:
- Running locally
- Using VPN
- Accessing from residential networks

## Testing

To verify if a host is blocked:

```bash
# Test from your server
curl -X POST https://rezka.ag/ajax/get_cdn_series/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "id=79810&translator_id=549&action=get_episodes"

# Check if response['url'] is a string or false
```

## Current Status

The code now:
1. ✓ Uses custom local HdRezkaApi library (not pip package)
2. ✓ Has session/cookie persistence
3. ✓ Has detailed error logging
4. ✓ Provides clear error messages about IP blocking
5. ✗ **Still blocked on Render.com due to IP detection**

## Next Steps

1. **Test on different hosting platform** (Railway, Fly.io)
2. **If that fails**: Implement proxy service (paid)
3. **If budget constrained**: Document as residential-only app
