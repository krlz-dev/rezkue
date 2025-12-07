# HDRezka API Documentation
## Based on Network Traffic Analysis

### Base URL
```
https://rezka.ag
```

## Search API

### Search for Content
```
GET /search/?do=search&subaction=search&q={QUERY}
```

Returns HTML with search results in `.b-content__inline_item` elements.

**Response Structure:**
- Title: `.b-content__inline_item-link a`
- URL: `.b-content__inline_item-link a[href]`
- Poster: `.b-content__inline_item-cover img[src]`
- Info: `.b-content__inline_item-link div` (year, country, genre)

## Video Page API

### Get Translations & Seasons
```
POST /ajax/get_cdn_series/

Parameters:
  - id: video ID (extracted from URL)
  - translator_id: translator/voice-over ID
  - favs: client UUID/fingerprint
  - action: "get_episodes"
```

**Response (JSON):**
```json
{
  "success": true,
  "seasons": "<li class='b-simple_season__item' data-tab_id='1'>Season 1</li>...",
  "episodes": "<li class='b-simple_episode__item' data-episode_id='1'>Episode 1</li>...",
  "url": "...",
  "quality": "...",
  "subtitle": "...",
  "thumbnails": "..."
}
```

### Get Episodes for Specific Season
```
POST /ajax/get_cdn_series/

Parameters:
  - id: video ID
  - translator_id: translator ID
  - season: season number
  - favs: client UUID
```

**Response:** Returns episodes HTML for that specific season.

### Get Stream URL
```
POST /ajax/get_cdn_series/

Parameters:
  - id: video ID
  - translator_id: translator ID
  - season: season number (for series)
  - episode: episode number (for series)
  - favs: client UUID
  - action: "get_stream"
```

**Response (JSON):**
```json
{
  "success": true,
  "url": "#hWzM2MHBdaHR0cHM6Ly9zdHJl...",  // Encoded URL
  "quality": "[360p]https://...[/360p][720p]https://...[/720p]",
  "subtitle": "subtitle data",
  "subtitle_lns": "subtitle languages",
  "thumbnails": "VTT thumbnail file URL"
}
```

**Note:** The `url` field is base64-encoded with custom encoding. It contains the HLS manifest URL.

## Other Endpoints

### Live Search (Autocomplete)
```
POST /engine/ajax/search.php

Parameters:
  - q: search query
```

Returns HTML with live search suggestions.

### Video Comments
```
GET /ajax/get_comments/

Parameters:
  - t: timestamp
  - news_id: video ID
  - cstart: comment page
  - type: comment type
  - comment_id: parent comment ID (0 for top-level)
  - skin: theme (hdrezka)
```

### Thumbnail Tiles
```
GET /ajax/get_cdn_tiles/{type}/{id}/?t={timestamp}
```

Returns WebVTT format file with thumbnail previews for video scrubbing.

## CDN Servers

Stream URLs are served from `*.stream.voidboost.cc` CDN servers:
- `stream.voidboost.cc`
- `apollo.stream.voidboost.cc`
- `green.stream.voidboost.cc`
- `midgard.stream.voidboost.cc`
- `monoceros.stream.voidboost.cc`

## Video Format

- **Protocol:** HLS (HTTP Live Streaming)
- **Manifest:** `.m3u8` files
- **Segments:** `.ts` chunks
- **Qualities:** Multiple (360p, 480p, 720p, 1080p, etc.)

## URL Structure

### Movie URL Pattern
```
/films/{genre}/{id}-{slug}.html
Example: /films/fiction/647-avatar-2009-latest.html
```

### Series URL Pattern
```
/series/{genre}/{id}-{slug}.html
Example: /series/comedy/1914-parki-i-zony-otdyha-2009.html
```

### Extract Video ID
```javascript
// Pattern: /{type}/{genre}/{ID}-{name}.html
const match = url.match(/\/(\d+)-/);
const videoId = match[1]; // e.g., "1914"
```

## Important Notes

1. **favs Parameter:** Generate a UUID v4 for the client fingerprint:
   ```python
   import uuid
   favs_id = str(uuid.uuid4())
   ```

2. **Stream URL Encoding:** The returned `url` is custom-encoded. You may need to:
   - Strip the leading `#`
   - Decode base64
   - Handle custom character replacements

3. **Session Management:** Use persistent session with proper headers:
   ```python
   headers = {
       'User-Agent': 'Mozilla/5.0 ...',
       'Accept-Language': 'en-US,en;q=0.9',
       'Referer': 'https://rezka.ag'
   }
   ```

4. **Time-Limited URLs:** Stream URLs expire after some time (~24 hours).

5. **Blocked Resources:** Block these to avoid overlays:
   - `code.21wiz.com/ovpaid.php`
   - Yandex Metrica
   - Analytics scripts

## Example Workflow

### For a Series:

1. **Search:**
   ```
   GET /search/?do=search&subaction=search&q=parks
   ```

2. **Get Video Page Info:**
   ```
   GET /series/comedy/1914-parki-i-zony-otdyha-2009.html
   Parse: video_id=1914, translator options
   ```

3. **Get Seasons & Episodes:**
   ```
   POST /ajax/get_cdn_series/
   {id: 1914, translator_id: 238, favs: uuid, action: "get_episodes"}
   ```

4. **Select Season (get episodes):**
   ```
   POST /ajax/get_cdn_series/
   {id: 1914, translator_id: 238, season: 2, favs: uuid}
   ```

5. **Get Stream URL:**
   ```
   POST /ajax/get_cdn_series/
   {id: 1914, translator_id: 238, season: 2, episode: 1, favs: uuid, action: "get_stream"}
   ```

6. **Play:**
   Decode the URL and load it in HLS player (Video.js, hls.js, etc.)

## Translation Detection

- **Original Voice:** Look for "Оригинал" or "Original" in translator name
- **Subtitles:** Check `subtitle` and `subtitle_lns` fields in stream response
- **Default:** Usually translator with `data-original="1"` attribute

---

**Last Updated:** 2025-12-07
**Based on:** Manual capture session and network analysis
