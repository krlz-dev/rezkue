#!/usr/bin/env python3
"""
Flask API Server for HDRezka using HdRezkaApi library
Provides search and video source extraction with proper quality handling
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from HdRezkaApi import HdRezkaApi
try:
    from HdRezkaApi import HdRezkaSearch
except ImportError:
    # Fallback for older versions
    HdRezkaSearch = None

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

BASE_URL = "https://rezka.ag"


@app.route('/api/search', methods=['GET'])
def search():
    """Search for videos using HdRezkaApi or fallback to BeautifulSoup"""
    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': 'Query parameter required'}), 400

    try:
        print(f"[SEARCH] Query: {query}")

        # Try using HdRezkaSearch if available
        if HdRezkaSearch:
            try:
                search_api = HdRezkaSearch(BASE_URL)
                results_raw = search_api(query)

                # Transform results to match our frontend format
                results = []
                for item in results_raw:
                    try:
                        # Extract video ID from URL
                        url = item.get('url', '')
                        video_id = extract_video_id(url)

                        results.append({
                            'id': video_id,
                            'title': item.get('title', 'Unknown'),
                            'url': url,
                            'poster': '',
                            'year': '',
                            'country': '',
                            'genre': '',
                            'info': f"Rating: {item.get('rating', 'N/A')}"
                        })
                    except Exception as e:
                        print(f"[ERROR] Parsing search result: {e}")
                        continue

                print(f"[SEARCH] Found {len(results)} results")
                return jsonify({
                    'query': query,
                    'count': len(results),
                    'results': results
                })
            except Exception as search_error:
                print(f"[WARNING] HdRezkaSearch failed: {search_error}, falling back to BeautifulSoup")

        # Fallback to manual BeautifulSoup parsing
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import quote

        search_url = f"{BASE_URL}/search/?do=search&subaction=search&q={quote(query)}"
        print(f"[SEARCH FALLBACK] {search_url}")

        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        items = soup.select('.b-content__inline_item')

        for item in items:
            try:
                link_elem = item.select_one('.b-content__inline_item-link a')
                if not link_elem:
                    continue

                url = link_elem.get('href')
                title = link_elem.text.strip()

                # Get additional info
                info_elem = item.select_one('.b-content__inline_item-link div')
                info = info_elem.text.strip() if info_elem else ''

                # Get poster image
                cover_elem = item.select_one('.b-content__inline_item-cover img')
                poster = cover_elem.get('src') if cover_elem else ''

                # Extract video ID from URL
                video_id = extract_video_id(url)

                results.append({
                    'id': video_id,
                    'title': title,
                    'url': url,
                    'poster': poster,
                    'year': '',
                    'country': '',
                    'genre': '',
                    'info': info
                })
            except Exception as e:
                print(f"[ERROR] Parsing item: {e}")
                continue

        print(f"[SEARCH] Found {len(results)} results")
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/video_page', methods=['POST'])
def get_video_page():
    """Get video page details using HdRezkaApi"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    try:
        print(f"[FETCH] Video page: {url}")

        # Initialize HdRezkaApi with the video URL
        rezka = HdRezkaApi(url)

        info = {
            'url': url,
            'title': rezka.name,
            'description': '',
            'type': rezka.type,
            'translations': [],
            'seasons': [],
            'video_id': extract_video_id(url),
            'default_translator': None,
            'thumbnail': rezka.thumbnail if hasattr(rezka, 'thumbnail') else '',
            'rating': str(rezka.rating) if hasattr(rezka, 'rating') else ''
        }

        # Get translators - in v7.1.0, translators is {name: id}
        translators = rezka.translators
        for trans_name, trans_id in translators.items():
            # Check if this is original voice
            is_original = 'оригинал' in trans_name.lower() or 'original' in trans_name.lower()

            info['translations'].append({
                'id': str(trans_id),
                'name': trans_name,
                'is_original': is_original
            })

        # Set default translator (original if found, otherwise first)
        if translators:
            default_trans = None
            # Try to find original voice first
            for trans_name, trans_id in translators.items():
                if 'оригинал' in trans_name.lower() or 'original' in trans_name.lower():
                    default_trans = str(trans_id)
                    break

            # If no original found, use first translator
            if not default_trans:
                default_trans = str(list(translators.values())[0])

            info['default_translator'] = default_trans

        # Get seasons if it's a series
        if rezka.type == 'tv_series':
            info['type'] = 'series'  # Convert to our frontend naming

            # Get seasons from seriesInfo (use first translator's data)
            if hasattr(rezka, 'seriesInfo') and rezka.seriesInfo:
                first_translator = list(rezka.seriesInfo.keys())[0]
                seasons_data = rezka.seriesInfo[first_translator].get('seasons', {})

                for season_num in sorted(seasons_data.keys()):
                    info['seasons'].append({
                        'id': str(season_num),
                        'number': f"Season {season_num}"
                    })
        elif rezka.type == 'film':
            info['type'] = 'movie'
        else:
            info['type'] = 'movie'  # Default fallback

        print(f"[SUCCESS] Got video info: {rezka.name} ({info['type']})")
        print(f"  Translators: {len(info['translations'])}")
        print(f"  Seasons: {len(info['seasons'])}")

        return jsonify(info)

    except Exception as e:
        print(f"[ERROR] Getting video page: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/episodes', methods=['POST'])
def get_episodes():
    """Get episodes for a series (first season by default)"""
    data = request.get_json()
    video_url = data.get('video_url')
    translator_id = data.get('translator_id')

    if not video_url:
        return jsonify({'error': 'video_url required'}), 400

    try:
        print(f"[EPISODES] Getting episodes for: {video_url}")

        rezka = HdRezkaApi(video_url)

        if rezka.type != 'tv_series':
            return jsonify({
                'success': False,
                'error': 'Not a series'
            }), 400

        # Get seriesInfo
        if not hasattr(rezka, 'seriesInfo') or not rezka.seriesInfo:
            return jsonify({
                'success': False,
                'error': 'No series info found'
            }), 404

        # Find translator by ID or use first
        translator_name = None
        if translator_id:
            # Find translator name by ID
            for name, tid in rezka.translators.items():
                if str(tid) == str(translator_id):
                    translator_name = name
                    break

        # If not found, use first translator
        if not translator_name:
            translator_name = list(rezka.seriesInfo.keys())[0]

        series_data = rezka.seriesInfo[translator_name]
        seasons_data = series_data.get('seasons', {})
        episodes_data = series_data.get('episodes', {})

        # Format all seasons
        seasons_formatted = [
            {'id': str(s), 'number': f"Season {s}"}
            for s in sorted(seasons_data.keys())
        ]

        # Get first season episodes
        if seasons_data:
            first_season = sorted(seasons_data.keys())[0]
            first_season_episodes = episodes_data.get(first_season, {})

            episodes_formatted = [
                {'id': str(ep), 'number': f"Episode {ep}"}
                for ep in sorted(first_season_episodes.keys())
            ]
        else:
            episodes_formatted = []

        print(f"[SUCCESS] Found {len(seasons_formatted)} seasons, {len(episodes_formatted)} episodes in season 1")

        return jsonify({
            'success': True,
            'seasons': seasons_formatted,
            'episodes': episodes_formatted
        })

    except Exception as e:
        print(f"[ERROR] Getting episodes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/season_episodes', methods=['POST'])
def get_season_episodes():
    """Get episodes for a specific season"""
    data = request.get_json()
    video_url = data.get('video_url')
    season_id = data.get('season_id')
    translator_id = data.get('translator_id')

    if not video_url or not season_id:
        return jsonify({'error': 'video_url and season_id required'}), 400

    try:
        print(f"[SEASON_EPISODES] Getting episodes for season {season_id}")

        rezka = HdRezkaApi(video_url)

        if rezka.type != 'tv_series':
            return jsonify({
                'success': False,
                'error': 'Not a series'
            }), 400

        # Get seriesInfo
        if not hasattr(rezka, 'seriesInfo') or not rezka.seriesInfo:
            return jsonify({
                'success': False,
                'error': 'No series info found'
            }), 404

        # Find translator by ID or use first
        translator_name = None
        if translator_id:
            for name, tid in rezka.translators.items():
                if str(tid) == str(translator_id):
                    translator_name = name
                    break

        if not translator_name:
            translator_name = list(rezka.seriesInfo.keys())[0]

        series_data = rezka.seriesInfo[translator_name]
        episodes_data = series_data.get('episodes', {})

        # Get episodes for the specified season
        season_num = int(season_id)
        season_episodes = episodes_data.get(season_num, {})

        if not season_episodes:
            return jsonify({
                'success': False,
                'error': f'Season {season_num} not found'
            }), 404

        # Format episodes
        episodes_formatted = [
            {'id': str(ep), 'number': f"Episode {ep}"}
            for ep in sorted(season_episodes.keys())
        ]

        print(f"[SUCCESS] Found {len(episodes_formatted)} episodes in season {season_num}")

        return jsonify({
            'success': True,
            'episodes': episodes_formatted,
            'season_id': season_id
        })

    except Exception as e:
        print(f"[ERROR] Getting season episodes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream', methods=['POST'])
def get_stream_url():
    """Get stream URLs with all quality options"""
    data = request.get_json()
    video_url = data.get('video_url')
    translator_id = data.get('translator_id')
    season_id = data.get('season_id', '')
    episode_id = data.get('episode_id', '')

    if not video_url:
        return jsonify({'error': 'video_url required'}), 400

    try:
        print(f"[STREAM] Getting stream for: {video_url}")
        print(f"  Translator: {translator_id}, Season: {season_id}, Episode: {episode_id}")

        rezka = HdRezkaApi(video_url)

        # Get the stream based on video type
        stream = None
        if rezka.type == 'tv_series':
            # Series - need season and episode
            if not season_id or not episode_id or season_id == 'null' or episode_id == 'null':
                return jsonify({
                    'success': False,
                    'error': 'Season and episode required for series'
                }), 400

            season_num = int(season_id)
            episode_num = int(episode_id)

            # Get stream - translator ID must be int if provided
            if translator_id and translator_id != 'null':
                stream = rezka.getStream(season=str(season_num), episode=str(episode_num), translation=int(translator_id))
            else:
                stream = rezka.getStream(season=str(season_num), episode=str(episode_num))
        else:
            # Movie - no season/episode needed
            if translator_id and translator_id != 'null':
                stream = rezka.getStream(translation=int(translator_id))
            else:
                stream = rezka.getStream()

        if not stream:
            return jsonify({
                'success': False,
                'error': 'Failed to get stream'
            }), 500

        # Get all available quality options
        quality_options = []

        # The stream.videos is a dict with quality as key
        if hasattr(stream, 'videos') and stream.videos:
            for quality, urls in stream.videos.items():
                # urls is a list of URLs for this quality
                if urls and len(urls) > 0:
                    quality_options.append({
                        'quality': quality,
                        'url': urls[0]  # Take first URL
                    })

            print(f"[SUCCESS] Found {len(quality_options)} quality options")

            # Format the response to match our frontend expectations
            # Create a quality field with [quality]url format
            quality_field = ','.join([
                f"[{opt['quality']}]{opt['url']}"
                for opt in quality_options
            ])

            return jsonify({
                'success': True,
                'url': quality_field,  # Put all quality options in url field
                'quality': quality_field,
                'qualities': quality_options,  # Also provide structured format
                'subtitle': '',
                'subtitle_lns': '',
                'thumbnails': ''
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No quality options found'
            }), 500

    except Exception as e:
        print(f"[ERROR] Getting stream: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def extract_video_id(url):
    """Extract video ID from URL"""
    import re
    # URL pattern: /films/fiction/2259-interstellar-2014.html
    match = re.search(r'/(\d+)-', url)
    if match:
        return match.group(1)
    return None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'HDRezka API (HdRezkaApi library)'})


if __name__ == '__main__':
    print("="*60)
    print("HDRezka API Server (Using HdRezkaApi Library)")
    print("="*60)
    print("Starting server on http://localhost:5001")
    print("\nEndpoints:")
    print("  GET  /api/search?q=QUERY")
    print("  POST /api/video_page (body: {url: '...'})")
    print("  POST /api/episodes (body: {video_url: '...'})")
    print("  POST /api/season_episodes (body: {video_url: '...', season_id: '...'})")
    print("  POST /api/stream (body: {video_url: '...', translator_id: '...', ...})")
    print("  GET  /health")
    print("="*60)
    print("\n✨ Now using HdRezkaApi library for reliable access!")
    print("   - No more anti-bot blocking")
    print("   - Proper stream URL decoding")
    print("   - Season/episode switching works!")
    print("="*60)

    app.run(debug=True, port=5001)
