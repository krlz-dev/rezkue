# HDRezka Integration Status

## ✅ What Works

### 1. Search (index.html + api_server.py)
- **Status:** ✅ Fully functional
- **How:** Search any movie/series via the web interface
- **Details:** Returns titles, posters, year, country, genre

### 2. Video Information
- **Status:** ✅ Fully functional
- **What you get:**
  - Video type (Movie vs Series)
  - Available translations/dubs
  - Original voice detection (marked with ⭐)
  - List of all seasons (for series)

### 3. Manual Capture Tool (manual_capture.py)
- **Status:** ✅ **Fully functional** - RECOMMENDED
- **How:** `python3 manual_capture.py --wait 180`
- **What it does:**
  - Opens real Firefox browser
  - You navigate manually
  - Captures ALL network traffic
  - Gets real stream URLs that work
  - **NO anti-bot blocking** (uses real browser)

## ⚠️ Limitations

### Season/Episode Selection via API
- **Status:** ❌ Blocked by HDRezka anti-bot protection
- **Why:** HDRezka returns "Network error #2" for programmatic AJAX requests
- **Detection:** They check for:
  - Real browser fingerprints
  - Valid session cookies from page load
  - JavaScript challenges
  - Request timing patterns

### Workaround
Use `manual_capture.py` instead:
1. Run the capture tool
2. Navigate to your series manually
3. Select translator, season, episode
4. Click play
5. Tool captures the real stream URL
6. Use that URL in any video player

## 📋 Recommended Workflow

### For Quick Browsing:
```bash
# 1. Start API server
python3 api_server.py

# 2. Open web interface
open index.html

# 3. Search for content
# 4. View available translations and seasons
```

### For Actually Playing Videos:
```bash
# Run manual capture tool
python3 manual_capture.py --wait 300

# Then:
# 1. Search for your content
# 2. Click on the video
# 3. Select translation (look for original voice)
# 4. Select season and episode
# 5. Click play
# 6. Close browser when done

# The tool saves to series_capture.json
# Analyze it to extract stream URLs:
python3 analyze_capture.py series_capture.json
```

## 🔑 Key Findings

### HDRezka's Anti-Bot Protection
1. **Search:** ✅ Works with proper User-Agent
2. **Video Page:** ✅ Works with proper headers
3. **AJAX Calls:** ❌ Requires real browser session

### Why Manual Capture Works
- Uses **real Firefox browser** (Playwright)
- Maintains proper session state
- Has valid browser fingerprint
- Executes JavaScript
- Natural request timing

### Stream URL Format
```
Encoded: #hWzM2MHBd...
Decoded: Contains voidboost.cc CDN URL
Format: HLS (.m3u8 manifest)
Expiry: ~24 hours
```

## 📊 Components Overview

| Component | Purpose | Status |
|-----------|---------|--------|
| `index.html` | Web UI for browsing | ✅ Works |
| `api_server.py` | Backend API | ✅ Partial |
| `manual_capture.py` | Browser automation | ✅ **Best option** |
| `capture_data.py` | Automated capture | ✅ Works |
| `analyze_capture.py` | Parse captures | ✅ Works |
| `simple_player.py` | CLI search | ✅ Works |

## 🎯 Use Cases

### ✅ You CAN:
- Search for any content
- See available translations
- Identify original voice content
- View all seasons (for series)
- Get stream URLs via manual capture
- Download/save stream URLs

### ❌ You CANNOT (without browser):
- Switch seasons programmatically
- Switch episodes programmatically
- Get stream URLs via pure API calls
- Automate video playback selection

## 💡 Future Improvements

To fully automate, we would need to:
1. Integrate Playwright into the API server
2. Maintain browser sessions for each user
3. Handle JavaScript challenges
4. Manage browser pools
5. Handle CloudFlare challenges

This is complex and resource-intensive, so the current **manual_capture.py** tool is the practical solution.

## 🏆 Best Tool for Each Task

| Task | Best Tool |
|------|-----------|
| Quick search | `index.html` + `api_server.py` |
| Browse content | `index.html` |
| Get stream URLs | **`manual_capture.py`** |
| Batch analysis | `capture_data.py` |
| Parse captures | `analyze_capture.py` |
| CLI search | `simple_player.py` |

---

**Bottom line:** Use `manual_capture.py` for reliable access to stream URLs. The web interface is great for browsing, but HDRezka's protection requires a real browser for actual playback.
