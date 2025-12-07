"""
Video controller - video player and details
"""
from flask import Blueprint, render_template, request
from HdRezkaApi import HdRezkaApi
from app.models import Video, Translator, Season, extract_video_id

video_bp = Blueprint('video', __name__)


@video_bp.route('/watch')
def watch():
    """Video player page"""
    url = request.args.get('url', '')
    title = request.args.get('title', 'Video Player')

    if not url:
        return render_template('index.html', error='No video URL provided')

    try:
        print(f"[WATCH] Loading video: {url}")

        # Initialize HdRezkaApi
        rezka = HdRezkaApi(url)

        # Build Video model
        video = Video(
            id=extract_video_id(url),
            title=rezka.name,
            url=url,
            type='series' if rezka.type == 'tv_series' else 'movie',
            thumbnail=rezka.thumbnail if hasattr(rezka, 'thumbnail') else None,
            rating=str(rezka.rating) if hasattr(rezka, 'rating') else None,
            translators=[],
            seasons=[]
        )

        # Get translators
        translators = rezka.translators
        for trans_name, trans_id in translators.items():
            is_original = 'оригинал' in trans_name.lower() or 'original' in trans_name.lower()
            video.translators.append(Translator(
                id=str(trans_id),
                name=trans_name,
                is_original=is_original
            ))

        # Set default translator (original if found, otherwise first)
        if translators:
            default_trans = None
            for trans_name, trans_id in translators.items():
                if 'оригинал' in trans_name.lower() or 'original' in trans_name.lower():
                    default_trans = str(trans_id)
                    break
            if not default_trans:
                default_trans = str(list(translators.values())[0])
            video.default_translator = default_trans

        # Get seasons if it's a series
        if rezka.type == 'tv_series':
            if hasattr(rezka, 'seriesInfo') and rezka.seriesInfo:
                first_translator = list(rezka.seriesInfo.keys())[0]
                seasons_data = rezka.seriesInfo[first_translator].get('seasons', {})

                for season_num in sorted(seasons_data.keys()):
                    video.seasons.append(Season(
                        id=str(season_num),
                        number=f"Season {season_num}"
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
