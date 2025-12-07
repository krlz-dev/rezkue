# Rezkue - HDRezka Player

A modern, minimalistic web application for browsing and streaming content from HDRezka. Built with Flask MVC architecture and dark teal theme.

## 🎯 Features

- **🔍 Search** - Find movies and TV series with poster images
- **🎬 Stream Player** - Watch content with HLS streaming
- **🎚️ Quality Selection** - Choose from multiple video quality options (360p - 1080p Ultra)
- **🗣️ Translation Support** - Select audio tracks, with original voice detection (⭐)
- **📺 Season/Episode Navigation** - Easy browsing for TV series
- **🎨 Dark Teal Design** - Minimalistic UI with smooth gradients
- **🖼️ Poster Images** - Visual thumbnails for all content
- **⭐ Rating Display** - See ratings for movies and series
- **🚫 Ad Blocking** - Automatically blocks ovpaid.php overlays (in capture tools)

## 🏗️ Technology Stack

- **Backend**: Flask (Python 3) with MVC architecture
- **Frontend**: Jinja2 templates with Tailwind CSS
- **Video Player**: Video.js with HLS support
- **API Integration**: HdRezkaApi library v7.1.0
- **Automation Tools**: Playwright (for capture scripts)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:krlz-dev/rezkue.git
   cd rezkue
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install Playwright browsers** (optional, for capture tools):
   ```bash
   python3 -m playwright install firefox
   ```

## 🚀 Quick Start

### Run the MVC Web Application (Recommended)

```bash
python3 run.py
```

Then open in your browser:
```
http://localhost:5001
```

**Features:**
- ✅ Search videos directly from rezka.ag
- ✅ View available translations (⭐ indicates original voice)
- ✅ Play videos with HLS streaming
- ✅ Select video quality (360p to 1080p Ultra)
- ✅ Browse seasons and episodes for TV series
- ✅ Modern dark teal minimalistic design
- ✅ Fully responsive layout

### Alternative: Network Capture Tools

If you need to manually capture network traffic:

```bash
# Manual capture with browser control
python3 manual_capture.py --wait 180

# Automated capture
python3 capture_data.py --search "Interstellar" --wait 10
```

**What capture tools do:**
- ✅ Opens real Firefox browser
- ✅ Captures video source URLs (.m3u8 manifests)
- ✅ Captures HLS segment URLs (.ts files)
- ✅ Captures API endpoints
- ✅ Blocks ovpaid.php overlays automatically

## 📊 Analysis Tools

Analyze captured network data:

```bash
python3 analyze_capture.py network_capture.json
```

Output includes:
- Video CDN domains
- HLS manifest URLs
- API endpoints discovered
- URL patterns for search/playback

## 🎬 How It Works

### Search Flow

1. **User searches** → `https://rezka.ag/search/?do=search&subaction=search&q=QUERY`
2. **Parse HTML** → Extract video titles, posters, metadata
3. **Open video page** → Fetch translation options
4. **Detect original voice** → Filter for "Оригинал" or "Original"

### Video Playback Flow

1. **Browser automation** → Navigate to video page
2. **Click play** → Triggers AJAX call to `/ajax/get_cdn_series/`
3. **Extract manifest** → Get HLS .m3u8 URL
4. **Stream via CDN** → `*.stream.voidboost.cc`

### CDN Servers Discovered

- `apollo.stream.voidboost.cc`
- `green.stream.voidboost.cc`
- `midgard.stream.voidboost.cc`
- `monoceros.stream.voidboost.cc`
- `stream.voidboost.cc`

## 🔧 Configuration

### Capture Script Options

```bash
python3 capture_data.py [OPTIONS]

Options:
  --url URL          Base URL (default: https://rezka.ag/)
  --search QUERY     Search query
  --wait SECONDS     Wait time for content (default: 10)
  --output FILE      Output JSON file (default: network_capture.json)
```

### Ad/Overlay Blocking

Automatically blocks:
- `code.21wiz.com/ovpaid.php`
- `cdn.jsdelivr.net/npm/yandex-metrica-watch/tag.js`
- Analytics and tracking scripts

## 📁 Project Structure

```
rezkue/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Data models (Video, Season, Episode, etc.)
│   ├── controllers/         # MVC Controllers
│   │   ├── main.py         # Home and search routes
│   │   ├── video.py        # Video player routes
│   │   └── api.py          # AJAX API endpoints
│   └── templates/           # Jinja2 templates
│       ├── base.html       # Base template with dark teal design
│       ├── index.html      # Search page
│       └── video.html      # Video player page
├── config.py                # Application configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
│
├── Legacy/Helper Tools:
├── index.html              # Original standalone web player
├── api_server.py           # Legacy standalone API server
├── capture_data.py         # Automated network capture
├── manual_capture.py       # Manual browser capture
├── analyze_capture.py      # Traffic analysis tool
└── simple_player.py        # CLI search client
```

## 🎨 MVC Web Application Features

The new Flask MVC application (`run.py`) includes:

- **Server-Side Rendering** - Jinja2 templates for better performance
- **MVC Architecture** - Clean separation of concerns
- **Dark Teal Theme** - Minimalistic design with white text
- **Video.js Player** - Full HLS streaming support
- **Translation Selection** - ⭐ indicates original voice
- **Quality Selector** - Auto-loads first quality, buttons to switch
- **Season/Episode Navigation** - Works perfectly with HdRezkaApi
- **Poster Images** - Visual thumbnails in search results
- **Rating Display** - Shows video ratings

## 🔍 Key Findings

### Search URL Pattern
```
https://rezka.ag/search/?do=search&subaction=search&q={query}
```

### Video Stream Format
- **Type**: HLS (HTTP Live Streaming)
- **Manifest**: `.m3u8` files
- **Segments**: `.ts` chunks
- **Encryption**: Time-based tokens in URLs

## 💻 Usage

### Search for Content
1. Start the application: `python3 run.py`
2. Open http://localhost:5001 in your browser
3. Enter a movie or series name in the search box
4. Click "Search"
5. Browse results with poster images and ratings

### Watch a Video
1. Click on any search result
2. Select your preferred translation (⭐ indicates original voice)
3. For TV series: select season and episode
4. Click "Play" button
5. Video auto-plays with first available quality
6. Use quality buttons below the player to switch resolution

### Change Quality
- Quality selector appears after clicking "Play"
- Click any quality button (360p, 480p, 720p, 1080p, 1080p Ultra)
- Video switches seamlessly

## 🌐 API Endpoints

### Web Routes
- `GET /` - Home page with search form
- `GET /search?q=QUERY` - Search results page
- `GET /watch?url=VIDEO_URL&title=TITLE` - Video player page
- `GET /health` - Health check

### AJAX API Routes
- `POST /api/episodes` - Get episodes for a series (first season)
- `POST /api/season_episodes` - Get episodes for specific season
- `POST /api/stream` - Get stream URLs with quality options

### HDRezka Original API (discovered)
```
POST /ajax/get_cdn_series/      # Get stream URLs
GET  /ajax/get_comments/        # Get comments
GET  /ajax/get_cdn_tiles/       # Get thumbnails
POST /engine/ajax/quick_content.php  # Quick preview
```

## 🛡️ Security & Privacy

- All requests use proper User-Agent headers
- CORS proxy for client-side fetching (allorigins.win)
- No credentials stored or transmitted
- Ad/tracker blocking built-in

## 📝 Notes

- Stream URLs are time-limited and expire
- Some videos require specific translation IDs
- CORS proxy may have rate limits
- Use capture tool for most reliable URL extraction

## 🤝 Contributing

This is a research/educational project for understanding video streaming APIs.

## ⚠️ Disclaimer

This tool is for educational purposes only. Respect copyright and terms of service.
