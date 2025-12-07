"""
API controller - AJAX endpoints for dynamic content
"""
import sys
import os

# Add local lib to path FIRST before any HdRezkaApi imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lib'))

from flask import Blueprint, jsonify, request
from app.models import Episode, Quality
import requests

# Now import HdRezkaApi from local lib
import HdRezkaApi
from HdRezkaApi import HdRezkaApi as HdRezkaApiClass
from HdRezkaApi import TVSeries, Movie, FetchFailed

print(f"[INIT] Using custom HdRezkaApi v{HdRezkaApi.__version__} library from lib/HdRezkaApi")

# Monkey-patch requests to log what's being sent
original_post = requests.post

def logged_post(url, *args, **kwargs):
    print(f"[HTTP] POST {url}")
    if 'headers' in kwargs:
        print(f"[HTTP] Headers: {kwargs['headers']}")
    if 'data' in kwargs:
        print(f"[HTTP] Data: {kwargs['data']}")
    response = original_post(url, *args, **kwargs)
    print(f"[HTTP] Response status: {response.status_code}")
    if hasattr(response, 'json'):
        try:
            json_resp = response.json()
            print(f"[HTTP] Response JSON keys: {list(json_resp.keys()) if isinstance(json_resp, dict) else 'not a dict'}")
            if isinstance(json_resp, dict) and 'url' in json_resp:
                print(f"[HTTP] Response['url'] type: {type(json_resp['url'])}, value: {json_resp['url']}")
        except:
            pass
    return response

requests.post = logged_post

api_bp = Blueprint('api', __name__)

# Browser-like headers to avoid detection/blocking
def get_headers(video_url='https://rezka.ag'):
    """Generate headers with proper Origin and Referer for AJAX requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://rezka.ag',
        'Referer': video_url,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'sec-ch-ua': '"Chromium";v="120", "Not(A:Brand";v="24", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

def get_cookies():
    """Get default cookies for API requests"""
    return {
        'hdmbbs': '1'  # Required cookie for API access
    }


@api_bp.route('/episodes', methods=['POST'])
def get_episodes():
    """Get episodes for a series (first season by default)"""
    data = request.get_json()
    video_url = data.get('video_url')
    translator_id = data.get('translator_id')

    if not video_url:
        return jsonify({'error': 'video_url required'}), 400

    try:
        print(f"[EPISODES] Getting episodes for: {video_url}")

        try:
            rezka = HdRezkaApiClass(video_url, headers=get_headers(video_url), cookies=get_cookies())
            print(f"[EPISODES] Content type: {rezka.type}")
            print(f"[EPISODES] Available translators: {list(rezka.translators.keys()) if hasattr(rezka, 'translators') else 'None'}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize HdRezkaApi: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Unable to access content. The source may be blocking requests or the URL is invalid.'
            }), 503

        if rezka.type != TVSeries():
            return jsonify({
                'success': False,
                'error': 'Not a series'
            }), 400

        # Get episodesInfo using new API
        if not hasattr(rezka, 'episodesInfo') or not rezka.episodesInfo:
            return jsonify({
                'success': False,
                'error': 'No series info found'
            }), 404

        # Format all seasons
        seasons_formatted = [
            {'id': str(season['season']), 'number': f"Season {season['season']}"}
            for season in rezka.episodesInfo
        ]

        # Get first season episodes
        if rezka.episodesInfo and len(rezka.episodesInfo) > 0:
            first_season = rezka.episodesInfo[0]
            episodes_formatted = [
                {'id': str(ep['episode']), 'number': f"Episode {ep['episode']}"}
                for ep in first_season['episodes']
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


@api_bp.route('/season_episodes', methods=['POST'])
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

        try:
            rezka = HdRezkaApiClass(video_url, headers=get_headers(video_url), cookies=get_cookies())
            print(f"[SEASON_EPISODES] Content type: {rezka.type}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize HdRezkaApi: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Unable to access content. The source may be blocking requests or the URL is invalid.'
            }), 503

        if rezka.type != TVSeries():
            return jsonify({
                'success': False,
                'error': 'Not a series'
            }), 400

        # Get episodesInfo
        if not hasattr(rezka, 'episodesInfo') or not rezka.episodesInfo:
            return jsonify({
                'success': False,
                'error': 'No series info found'
            }), 404

        # Get episodes for the specified season
        season_num = int(season_id)
        season_data = next((s for s in rezka.episodesInfo if s['season'] == season_num), None)

        if not season_data:
            return jsonify({
                'success': False,
                'error': f'Season {season_num} not found'
            }), 404

        # Format episodes
        episodes_formatted = [
            {'id': str(ep['episode']), 'number': f"Episode {ep['episode']}"}
            for ep in season_data['episodes']
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


@api_bp.route('/stream', methods=['POST'])
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

        # Initialize HdRezkaApi with proper headers and cookies
        try:
            headers = get_headers(video_url)
            cookies = get_cookies()
            print(f"[DEBUG] Headers being sent:")
            for key, value in headers.items():
                print(f"  {key}: {value}")
            print(f"[DEBUG] Cookies: {cookies}")

            rezka = HdRezkaApiClass(video_url, headers=headers, cookies=cookies)
            print(f"[STREAM] Content type: {rezka.type}")
            print(f"[STREAM] Available translators: {list(rezka.translators.keys()) if hasattr(rezka, 'translators') else 'None'}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize HdRezkaApi: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Unable to access content. The source may be blocking requests or the URL is invalid.'
            }), 503

        # Get the stream based on video type
        stream = None
        try:
            if rezka.type == TVSeries():
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
                    stream = rezka.getStream(season=season_num, episode=episode_num, translation=int(translator_id))
                else:
                    stream = rezka.getStream(season=season_num, episode=episode_num)
            else:
                # Movie - no season/episode needed
                if translator_id and translator_id != 'null':
                    stream = rezka.getStream(translation=int(translator_id))
                else:
                    stream = rezka.getStream()
        except FetchFailed as e:
            # This is raised when API returns success: true but url: false
            error_msg = str(e)
            print(f"[ERROR] FetchFailed: {error_msg}")
            print(f"[ERROR] This is likely IP-based blocking from datacenter/cloud hosting")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Unable to access video stream. The server is blocking requests from this IP address. See IP_BLOCKING_ISSUE.md for solutions.'
            }), 503
        except Exception as e:
            print(f"[ERROR] Failed to get stream: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to get stream: {str(e)}'
            }), 503

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

            # Extract subtitle information
            subtitles = []
            if hasattr(stream, 'subtitles') and hasattr(stream.subtitles, 'subtitles') and stream.subtitles.subtitles:
                for code, sub_info in stream.subtitles.subtitles.items():
                    subtitles.append({
                        'code': code,
                        'label': sub_info['title'],
                        'url': sub_info['link']
                    })
                print(f"[SUCCESS] Found {len(subtitles)} subtitle tracks")

            # Format the response
            quality_field = ','.join([
                f"[{opt['quality']}]{opt['url']}"
                for opt in quality_options
            ])

            return jsonify({
                'success': True,
                'url': quality_field,
                'quality': quality_field,
                'qualities': quality_options,
                'subtitles': subtitles,
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
