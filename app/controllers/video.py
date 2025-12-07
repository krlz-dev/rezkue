"""
Video controller - video player and details
"""
import sys
import os

# Add local lib to path FIRST before any HdRezkaApi imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lib'))

from flask import Blueprint, render_template, request
from HdRezkaApi import HdRezkaApi as HdRezkaApiClass
from HdRezkaApi import TVSeries, Movie
from app.models import Video, Translator, Season, extract_video_id

video_bp = Blueprint('video', __name__)

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


@video_bp.route('/watch')
def watch():
    """Video player page"""
    url = request.args.get('url', '')
    title = request.args.get('title', 'Video Player')

    if not url:
        return render_template('index.html', error='No video URL provided')

    try:
        print(f"[WATCH] Loading video: {url}")

        # Initialize HdRezkaApi with browser headers to avoid blocking
        rezka = HdRezkaApiClass(url, headers=BROWSER_HEADERS, cookies={'hdmbbs': '1'})

        # Build Video model
        video = Video(
            id=extract_video_id(url),
            title=rezka.name,
            url=url,
            type='series' if rezka.type == TVSeries() else 'movie',
            thumbnail=rezka.thumbnail if hasattr(rezka, 'thumbnail') else None,
            rating=str(rezka.rating) if hasattr(rezka, 'rating') else None,
            translators=[],
            seasons=[]
        )

        # Get translators (new API returns {translator_id: {"name": ..., "premium": ...}})
        translators = rezka.translators
        for trans_id, trans_data in translators.items():
            trans_name = trans_data['name'] if isinstance(trans_data, dict) else trans_data
            is_original = 'оригинал' in trans_name.lower() or 'original' in trans_name.lower()
            video.translators.append(Translator(
                id=str(trans_id),
                name=trans_name,
                is_original=is_original
            ))

        # Set default translator (original if found, otherwise first)
        if translators:
            default_trans = None
            for trans_id, trans_data in translators.items():
                trans_name = trans_data['name'] if isinstance(trans_data, dict) else trans_data
                if 'оригинал' in trans_name.lower() or 'original' in trans_name.lower():
                    default_trans = str(trans_id)
                    break
            if not default_trans:
                default_trans = str(list(translators.keys())[0])
            video.default_translator = default_trans

        # Get seasons if it's a series (use episodesInfo from new API)
        if rezka.type == TVSeries():
            if hasattr(rezka, 'episodesInfo') and rezka.episodesInfo:
                for season_data in rezka.episodesInfo:
                    video.seasons.append(Season(
                        id=str(season_data['season']),
                        number=f"Season {season_data['season']}"
                    ))

        print(f"[WATCH] Video loaded: {video.title} ({video.type})")
        print(f"  Translators: {len(video.translators)}")
        print(f"  Seasons: {len(video.seasons)}")

        return render_template('video.html', video=video)

    except Exception as e:
        print(f"[ERROR] Loading video: {e}")
        import traceback
        traceback.print_exc()
        return render_template('index.html', error=f"Failed to load video: {str(e)}")
