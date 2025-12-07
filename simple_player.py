#!/usr/bin/env python3
"""
Simple HDRezka Video Player Client
Demonstrates how to search, select, and play videos based on captured network patterns
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class HDRezkaClient:
    def __init__(self, base_url="https://rezka.ag"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })

    def search(self, query):
        """Search for videos"""
        search_url = f"{self.base_url}/search/?do=search&subaction=search&q={query}"

        print(f"\n[SEARCHING] {query}")
        print(f"[URL] {search_url}\n")

        response = self.session.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all video items
        results = []
        items = soup.select('.b-content__inline_item')

        for item in items:
            try:
                link = item.select_one('a')
                if not link:
                    continue

                url = link.get('href')
                title_elem = item.select_one('.b-content__inline_item-link a')
                title = title_elem.text.strip() if title_elem else 'Unknown'

                # Get additional info
                info_elem = item.select_one('.b-content__inline_item-link div')
                info = info_elem.text.strip() if info_elem else ''

                results.append({
                    'title': title,
                    'url': url,
                    'info': info
                })
            except Exception as e:
                continue

        return results

    def get_video_page_info(self, video_url):
        """Get video page information"""
        print(f"\n[FETCHING] Video page: {video_url}")

        response = self.session.get(video_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        info = {
            'url': video_url,
            'title': 'Unknown',
            'description': '',
            'player_data': {}
        }

        # Extract title
        title_elem = soup.select_one('.b-post__title h1')
        if title_elem:
            info['title'] = title_elem.text.strip()

        # Extract description
        desc_elem = soup.select_one('.b-post__description_text')
        if desc_elem:
            info['description'] = desc_elem.text.strip()[:200] + '...'

        # Try to extract player data from page
        # Look for data-id and other player-related attributes
        player_elem = soup.select_one('#cdnplayerfilms, #cdnplayerserials, [id*="player"]')
        if player_elem:
            info['player_data'] = {
                'data_id': player_elem.get('data-id'),
                'data_file': player_elem.get('data-file'),
                'player_id': player_elem.get('id')
            }

        return info

    def extract_video_id_from_url(self, url):
        """Extract video ID from URL"""
        # URL pattern: /films/fiction/2259-interstellar-2014.html
        match = re.search(r'/(\d+)-', url)
        if match:
            return match.group(1)
        return None


def main():
    """Demo the client"""
    import sys

    client = HDRezkaClient()

    # Get search query from command line or use default
    query = sys.argv[1] if len(sys.argv) > 1 else "Interstellar"

    print("="*60)
    print("HDRezka Simple Video Player Client")
    print("="*60)

    # Step 1: Search
    results = client.search(query)

    if not results:
        print("\n[ERROR] No results found!")
        return

    print(f"[FOUND] {len(results)} results:\n")
    for i, result in enumerate(results[:10], 1):
        print(f"{i}. {result['title']}")
        print(f"   Info: {result['info']}")
        print(f"   URL: {result['url']}\n")

    # Step 2: Get first video details
    if results:
        print("\n" + "="*60)
        print("GETTING VIDEO DETAILS (First Result)")
        print("="*60)

        video_url = results[0]['url']
        video_info = client.get_video_page_info(video_url)

        print(f"\nTitle: {video_info['title']}")
        print(f"Description: {video_info['description']}")
        print(f"\nPlayer Data:")
        for key, value in video_info['player_data'].items():
            if value:
                print(f"  {key}: {value}")

        video_id = client.extract_video_id_from_url(video_url)
        if video_id:
            print(f"\nExtracted Video ID: {video_id}")

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
To get the actual video stream URL, you would need to:

1. Call the AJAX endpoint:
   POST https://rezka.ag/ajax/get_cdn_series/

   With parameters extracted from the page (video ID, translator, etc.)

2. Parse the response to get the HLS manifest URL (.m3u8)

3. Use a video player that supports HLS to play the stream
   Examples:
   - VLC Media Player
   - mpv
   - ffplay
   - Browser with hls.js

4. Example command to play with mpv:
   mpv "https://stream.voidboost.cc/.../manifest.m3u8"

For a complete implementation, you'll need to:
- Capture the exact POST parameters sent to ajax/get_cdn_series/
- Handle different translators/qualities
- Implement proper session handling
    """)


if __name__ == '__main__':
    main()
