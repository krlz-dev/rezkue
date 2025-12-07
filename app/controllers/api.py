"""
API controller - AJAX endpoints for dynamic content
"""
from flask import Blueprint, jsonify, request
from HdRezkaApi import HdRezkaApi
from app.models import Episode, Quality

api_bp = Blueprint('api', __name__)

# Browser-like headers to avoid detection/blocking
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
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
            rezka = HdRezkaApi(video_url, headers=BROWSER_HEADERS)
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
            rezka = HdRezkaApi(video_url, headers=BROWSER_HEADERS)
            print(f"[SEASON_EPISODES] Content type: {rezka.type}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize HdRezkaApi: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Unable to access content. The source may be blocking requests or the URL is invalid.'
            }), 503

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

        try:
            rezka = HdRezkaApi(video_url, headers=BROWSER_HEADERS)
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
        except AttributeError as e:
            # This happens when the API request is blocked or returns invalid data
            print(f"[ERROR] API request failed - likely blocked by source: {e}")
            return jsonify({
                'success': False,
                'error': 'Unable to access video stream. The source may be blocking automated requests or the content is unavailable.'
            }), 503
        except Exception as e:
            print(f"[ERROR] Unexpected error getting stream: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to retrieve stream: {str(e)}'
            }), 500

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
