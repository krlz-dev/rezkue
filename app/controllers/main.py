"""
Main controller - home page and search
"""
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from HdRezkaApi import HdRezkaApi
try:
    from HdRezkaApi import HdRezkaSearch
except ImportError:
    HdRezkaSearch = None
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from app.models import SearchResult, extract_video_id
import os

main_bp = Blueprint('main', __name__)

BASE_URL = "https://rezka.ag"


@main_bp.route('/')
def index():
    """Home page with recently added content"""
    try:
        print("[HOME] Fetching recently added content from homepage")

        response = requests.get(BASE_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        # Get video items from homepage
        items = soup.select('.b-content__inline_item')

        for item in items[:24]:  # Limit to 24 items (4 rows of 6)
            try:
                link_elem = item.select_one('.b-content__inline_item-link a')
                if not link_elem:
                    continue

                url = link_elem.get('href')
                # Convert relative URLs to absolute
                if url and url.startswith('/'):
                    url = BASE_URL + url

                title = link_elem.text.strip()

                # Get additional info
                info_elem = item.select_one('.b-content__inline_item-link div')
                info = info_elem.text.strip() if info_elem else ''

                # Get poster image
                cover_elem = item.select_one('.b-content__inline_item-cover img')
                poster = cover_elem.get('src') if cover_elem else ''

                # Extract video ID
                video_id = extract_video_id(url)

                results.append(SearchResult(
                    id=video_id,
                    title=title,
                    url=url,
                    poster=poster,
                    year='',
                    country='',
                    genre='',
                    info=info
                ))
            except Exception as e:
                print(f"[ERROR] Parsing item: {e}")
                continue

        print(f"[HOME] Found {len(results)} recently added items")
        return render_template('index.html', results=results, is_homepage=True)

    except Exception as e:
        print(f"[ERROR] Fetching homepage: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to empty homepage
        return render_template('index.html')


@main_bp.route('/search')
def search():
    """Search for videos"""
    query = request.args.get('q', '')

    if not query:
        return render_template('index.html', error='Please enter a search query')

    try:
        print(f"[SEARCH] Query: {query}")

        # Try using HdRezkaSearch if available
        if HdRezkaSearch:
            try:
                search_api = HdRezkaSearch(BASE_URL)
                results_raw = search_api(query)

                # Transform results
                results = []
                for item in results_raw:
                    try:
                        url = item.get('url', '')
                        video_id = extract_video_id(url)

                        results.append(SearchResult(
                            id=video_id,
                            title=item.get('title', 'Unknown'),
                            url=url,
                            poster='',
                            year='',
                            country='',
                            genre='',
                            info=f"Rating: {item.get('rating', 'N/A')}"
                        ))
                    except Exception as e:
                        print(f"[ERROR] Parsing search result: {e}")
                        continue

                print(f"[SEARCH] Found {len(results)} results")
                return render_template('index.html', query=query, results=results)
            except Exception as search_error:
                print(f"[WARNING] HdRezkaSearch failed: {search_error}, falling back to BeautifulSoup")

        # Fallback to manual BeautifulSoup parsing
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

                # Extract video ID
                video_id = extract_video_id(url)

                results.append(SearchResult(
                    id=video_id,
                    title=title,
                    url=url,
                    poster=poster,
                    year='',
                    country='',
                    genre='',
                    info=info
                ))
            except Exception as e:
                print(f"[ERROR] Parsing item: {e}")
                continue

        print(f"[SEARCH] Found {len(results)} results")
        return render_template('index.html', query=query, results=results)

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        return render_template('index.html', error=f"Search error: {str(e)}")


@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'HDRezka MVC App (HdRezkaApi library)'})


@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for SEO"""
    try:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        return send_from_directory(static_dir, 'robots.txt', mimetype='text/plain')
    except Exception as e:
        print(f"[ERROR] Serving robots.txt: {e}")
        # Return a basic robots.txt if file not found
        return """User-agent: *
Allow: /
Disallow: /api/""", 200, {'Content-Type': 'text/plain'}
