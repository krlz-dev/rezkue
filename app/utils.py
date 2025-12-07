"""
Utility functions for bypassing API blocking
"""
import os
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class PlaywrightStreamFetcher:
    """
    Uses Playwright to fetch stream URLs when direct API calls are blocked.
    This uses a real browser to bypass bot detection.
    """

    @staticmethod
    def get_stream_with_browser(video_url, translator_id=None, season=None, episode=None):
        """
        Fetch stream URL using Playwright browser automation

        Args:
            video_url: URL of the video page
            translator_id: Optional translator/voice ID
            season: Optional season number (for series)
            episode: Optional episode number (for series)

        Returns:
            dict with 'success', 'qualities', 'subtitles' keys, or error info
        """
        print(f"[PLAYWRIGHT] Attempting to fetch stream with browser")
        print(f"  URL: {video_url}")
        print(f"  Translator: {translator_id}, Season: {season}, Episode: {episode}")

        try:
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )

                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US'
                )

                page = context.new_page()

                # Navigate to video page
                print(f"[PLAYWRIGHT] Navigating to {video_url}")
                page.goto(video_url, wait_until='networkidle', timeout=30000)

                # Wait for player to load
                page.wait_for_selector('#player', timeout=10000)

                # If translator is specified, select it
                if translator_id:
                    try:
                        # Click translator dropdown
                        page.click('.b-translator__item[data-translator_id="' + str(translator_id) + '"]', timeout=5000)
                        page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"[PLAYWRIGHT] Could not select translator: {e}")

                # If series, select season and episode
                if season and episode:
                    try:
                        # Select season
                        page.click(f'.b-simple_season__item[data-season_id="{season}"]', timeout=5000)
                        page.wait_for_timeout(500)

                        # Select episode
                        page.click(f'.b-simple_episode__item[data-episode_id="{episode}"]', timeout=5000)
                        page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"[PLAYWRIGHT] Could not select season/episode: {e}")

                # Intercept network requests to capture stream data
                stream_data = {'qualities': [], 'subtitles': []}

                def handle_response(response):
                    """Capture AJAX responses with stream URLs"""
                    if 'ajax' in response.url and response.status == 200:
                        try:
                            data = response.json()
                            if 'url' in data and data.get('success'):
                                # Parse quality URLs
                                url_str = data['url']
                                if url_str and '[' in url_str:
                                    # Format: [quality]url,[quality]url,...
                                    for part in url_str.split(','):
                                        if '[' in part and ']' in part:
                                            quality = part[part.index('[')+1:part.index(']')]
                                            url = part[part.index(']')+1:]
                                            stream_data['qualities'].append({
                                                'quality': quality,
                                                'url': url
                                            })

                                # Get subtitles if present
                                if 'subtitle' in data:
                                    stream_data['subtitles_raw'] = data.get('subtitle', '')

                        except Exception as e:
                            print(f"[PLAYWRIGHT] Error parsing response: {e}")

                page.on('response', handle_response)

                # Click play button to trigger stream request
                try:
                    page.click('.b-player__btn', timeout=5000)
                    page.wait_for_timeout(3000)  # Wait for AJAX request
                except Exception as e:
                    print(f"[PLAYWRIGHT] Could not click play: {e}")

                browser.close()

                if stream_data['qualities']:
                    print(f"[PLAYWRIGHT] Successfully captured {len(stream_data['qualities'])} quality options")
                    return {
                        'success': True,
                        'qualities': stream_data['qualities'],
                        'subtitles': stream_data.get('subtitles', [])
                    }
                else:
                    print(f"[PLAYWRIGHT] No stream data captured")
                    return {
                        'success': False,
                        'error': 'Could not capture stream data from browser'
                    }

        except PlaywrightTimeout as e:
            print(f"[PLAYWRIGHT] Timeout error: {e}")
            return {
                'success': False,
                'error': f'Browser automation timeout: {str(e)}'
            }
        except Exception as e:
            print(f"[PLAYWRIGHT] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Browser automation failed: {str(e)}'
            }
