# 🚀 Quick Start Guide

## Problem: CloudFlare Blocking

The site uses CloudFlare protection and blocks:
- ❌ CORS proxy requests
- ❌ Direct browser fetches
- ✅ **Solution**: Use our local API server with proper headers

## ⚡ 2-Step Setup

### Step 1: Start the API Server

```bash
python3 api_server.py
```

You should see:
```
============================================================
HDRezka API Server
============================================================
Starting server on http://localhost:5000
```

**Keep this terminal running!**

### Step 2: Open the Web Player

```bash
open index.html
```

Or just open `index.html` in your browser.

## 🎬 How to Use

1. **Search** - Type any movie name (e.g., "Interstellar") and press Enter
2. **View Results** - Click on any result to see available translations
3. **See Translations** - Green badges = Original voice, Blue = Dubbed
4. **Play Demo Videos** - Use the pre-loaded demos at the bottom

## 🔧 Alternative: Use the Capture Tool

If you need fresh stream URLs:

```bash
python3 capture_data.py --search "Interstellar" --wait 10
```

This will:
- ✅ Bypass ALL CloudFlare protection
- ✅ Block ovpaid.php overlays
- ✅ Capture real HLS stream URLs
- ✅ Extract all available translations

## 📊 Check What's Running

```bash
# Test API server
curl http://localhost:5000/health

# Should return: {"status":"ok","service":"HDRezka API"}
```

## 🛑 Stop Everything

```bash
# Find and kill Python processes
pkill -f "api_server.py"
pkill -f "capture_data.py"
```

## ⚙️ How It Works

### Architecture

```
Browser (index.html)
    ↓ fetch()
Local API Server (localhost:5000)
    ↓ requests with proper headers
rezka.ag Backend
    ↓ HTML response
Parse & Extract
    ↓ JSON
Browser displays results
```

### Why This Works

1. **Browser** → Can't bypass CORS
2. **CORS Proxy** → Blocked by CloudFlare
3. **Our API Server** → Uses proper User-Agent & headers ✅
4. **Capture Tool** → Real browser automation ✅

## 🎯 Best Workflow

For **searching and browsing**:
```bash
# Terminal 1
python3 api_server.py

# Browser
open index.html
```

For **getting actual stream URLs**:
```bash
# Terminal 2
python3 capture_data.py --search "Movie Name" --wait 10

# Then analyze
python3 analyze_capture.py network_capture.json
```

## 🔍 Troubleshooting

**Error: "Failed to fetch search results"**
- Make sure API server is running: `python3 api_server.py`
- Check server is on port 5000: `curl http://localhost:5000/health`

**No search results**
- The site might still block your IP
- Try the capture tool instead (uses real browser)
- Or use a VPN

**Video won't play**
- Stream URLs are time-limited (expire after ~24hrs)
- Run capture tool to get fresh URLs
- Use the URLs immediately

## 💡 Pro Tips

1. **Keep API server running** while browsing
2. **Use capture tool** for actual streaming URLs
3. **Original voice** = Green badges in search results
4. **Stream URLs expire** - get fresh ones daily

## 📁 Project Structure

```
index.html          → Web player (needs api_server.py)
api_server.py       → Backend API (bypass CloudFlare)
capture_data.py     → Browser automation (best for URLs)
analyze_capture.py  → Parse captured data
simple_player.py    → CLI search tool
```

Happy streaming! 🎬
