#!/usr/bin/env python3
"""
Network Traffic Capture Script for HDRezka
Captures and analyzes video source URLs and API endpoints
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs


class NetworkCapture:
    def __init__(self):
        self.requests = []
        self.responses = []
        self.video_sources = []
        self.api_calls = []

    async def should_block_request(self, route, request):
        """Block unwanted requests like ads, tracking, overlays"""
        url = request.url

        # List of patterns to block
        block_patterns = [
            'ovpaid.php',
            '/ads/',
            'doubleclick.net',
            'googlesyndication.com',
            'googleadservices.com',
            'adserver',
            'analytics',
            'tracking',
            'metric',
            'banner'
        ]

        # Check if URL should be blocked
        for pattern in block_patterns:
            if pattern in url.lower():
                print(f"[BLOCKED] {url}")
                await route.abort()
                return

        # Allow the request to continue
        await route.continue_()

    async def capture_request(self, request):
        """Capture outgoing requests"""
        url = request.url
        method = request.method

        try:
            headers = await request.all_headers()
        except:
            headers = {}

        request_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'method': method,
            'headers': headers,
            'resource_type': request.resource_type
        }

        self.requests.append(request_data)

        # Detect video-related requests
        if self._is_video_related(url, request.resource_type):
            print(f"[VIDEO] {method} {url}")
            self.video_sources.append(request_data)

        # Detect API calls
        if self._is_api_call(url):
            print(f"[API] {method} {url}")
            self.api_calls.append(request_data)

    async def capture_response(self, response):
        """Capture incoming responses"""
        url = response.url
        status = response.status
        headers = await response.all_headers()

        response_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status': status,
            'headers': headers,
            'resource_type': response.request.resource_type
        }

        # Try to capture response body for relevant requests
        if self._is_interesting_response(url, response.request.resource_type):
            try:
                if 'application/json' in headers.get('content-type', ''):
                    body = await response.text()
                    response_data['body'] = body
                    print(f"[JSON RESPONSE] {url[:100]}...")
            except Exception as e:
                response_data['body_error'] = str(e)

        self.responses.append(response_data)

    def _is_video_related(self, url, resource_type):
        """Check if URL is video-related"""
        video_patterns = [
            r'\.m3u8',
            r'\.mp4',
            r'\.webm',
            r'\.mkv',
            r'\.ts$',  # HLS segments
            r'/stream/',
            r'/video/',
            r'/manifest',
            r'/playlist'
        ]

        url_lower = url.lower()
        return (resource_type == 'media' or
                any(re.search(pattern, url_lower) for pattern in video_patterns))

    def _is_api_call(self, url):
        """Check if URL is an API call"""
        api_patterns = [
            r'/api/',
            r'/ajax/',
            r'\.json',
            r'/graphql',
            r'/v\d+/',  # versioned APIs
        ]

        return any(re.search(pattern, url.lower()) for pattern in api_patterns)

    def _is_interesting_response(self, url, resource_type):
        """Check if response should be captured"""
        return (self._is_api_call(url) or
                resource_type in ['xhr', 'fetch'] or
                '.json' in url.lower())

    def save_to_file(self, filename='network_capture.json'):
        """Save captured data to JSON file"""
        data = {
            'capture_time': datetime.now().isoformat(),
            'summary': {
                'total_requests': len(self.requests),
                'video_sources': len(self.video_sources),
                'api_calls': len(self.api_calls)
            },
            'video_sources': self.video_sources,
            'api_calls': self.api_calls,
            'all_requests': self.requests,
            'all_responses': self.responses
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] Data saved to {filename}")
        return data

    def print_summary(self):
        """Print summary of captured data"""
        print("\n" + "="*60)
        print("CAPTURE SUMMARY")
        print("="*60)
        print(f"Total Requests: {len(self.requests)}")
        print(f"Video Sources Found: {len(self.video_sources)}")
        print(f"API Calls Found: {len(self.api_calls)}")

        if self.video_sources:
            print("\n--- VIDEO SOURCES ---")
            for vs in self.video_sources:
                print(f"  - {vs['url']}")

        if self.api_calls:
            print("\n--- API ENDPOINTS ---")
            for api in self.api_calls:
                print(f"  - {api['method']} {api['url']}")

        # Extract unique domains
        domains = set()
        for req in self.requests:
            parsed = urlparse(req['url'])
            if parsed.netloc:
                domains.add(parsed.netloc)

        print("\n--- DOMAINS ACCESSED ---")
        for domain in sorted(domains):
            print(f"  - {domain}")


async def capture_site_traffic(url, search_query=None, wait_time=10):
    """
    Capture network traffic from the site

    Args:
        url: The URL to visit
        search_query: Optional search term to enter
        wait_time: How long to wait for content to load (seconds)
    """
    capture = NetworkCapture()

    async with async_playwright() as p:
        # Launch browser with stealth options
        # Try Firefox first, fall back to Chromium
        try:
            browser = await p.firefox.launch(
                headless=False
            )
        except:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )

        # Add stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = await context.new_page()

        # Set up request blocking for ads/overlays
        await page.route('**/*', capture.should_block_request)

        # Set up network listeners
        page.on('request', capture.capture_request)
        page.on('response', capture.capture_response)

        print(f"[NAVIGATING] {url}")

        try:
            # If search query provided, use direct search URL
            if search_query:
                search_url = f"{url.rstrip('/')}/search/?do=search&subaction=search&q={search_query}"
                print(f"[SEARCHING] {search_url}")
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                print("[LOADED] Search results loaded")
                await page.wait_for_timeout(2000)
            else:
                # Navigate to the site
                await page.goto(url, wait_until='networkidle', timeout=30000)
                print("[LOADED] Page loaded")

            # Wait for dynamic content to load
            print(f"[WAITING] Waiting {wait_time} seconds for content...")
            await page.wait_for_timeout(wait_time * 1000)

            # Try to click on first video if available
            print("[LOOKING] Searching for video elements...")
            video_selectors = [
                '.b-content__inline_item a',
                '.b-content__inline_item',
                'a[href*="/films/"]',
                'a[href*="/series/"]',
                '.movie-item'
            ]

            clicked_video = False
            for selector in video_selectors:
                try:
                    video_link = await page.query_selector(selector)
                    if video_link:
                        print(f"[FOUND] Video element: {selector}")
                        href = await video_link.get_attribute('href')
                        print(f"[INFO] Video URL: {href}")
                        await video_link.click()
                        print("[CLICKED] Opened video page")
                        await page.wait_for_load_state('networkidle', timeout=10000)
                        clicked_video = True
                        break
                except Exception as e:
                    print(f"[DEBUG] Failed with {selector}: {e}")
                    continue

            if clicked_video:
                # Look for play button and iframe
                await page.wait_for_timeout(3000)
                print("[LOOKING] Searching for video player...")

                # Try to find iframe first
                iframe_selectors = ['iframe[id*="player"]', 'iframe', '.b-player iframe']
                for iframe_sel in iframe_selectors:
                    try:
                        iframe = await page.query_selector(iframe_sel)
                        if iframe:
                            src = await iframe.get_attribute('src')
                            print(f"[FOUND] Iframe: {src}")
                    except:
                        pass

                # Look for play button
                play_selectors = [
                    '#pjax-container iframe',
                    '.b-player__play',
                    '[class*="play"]',
                    'button[class*="play"]',
                    '.video-player',
                    'video',
                    '#cdn-player'
                ]

                for play_sel in play_selectors:
                    try:
                        play_btn = await page.wait_for_selector(play_sel, timeout=3000)
                        if play_btn:
                            print(f"[FOUND] Play element: {play_sel}")
                            await play_btn.click()
                            print("[CLICKED] Started playback")
                            await page.wait_for_timeout(8000)
                            break
                    except Exception as e:
                        print(f"[DEBUG] No play button at {play_sel}")
                        continue

        except Exception as e:
            print(f"[ERROR] {e}")

        # Keep browser open a bit longer to capture all requests
        try:
            await page.wait_for_timeout(3000)
        except:
            pass

        try:
            await browser.close()
        except:
            print("[INFO] Browser already closed")

    return capture


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Capture network traffic from HDRezka')
    parser.add_argument('--url', default='https://rezka.ag/', help='URL to capture')
    parser.add_argument('--search', help='Search query to test')
    parser.add_argument('--wait', type=int, default=10, help='Wait time in seconds')
    parser.add_argument('--output', default='network_capture.json', help='Output JSON file')

    args = parser.parse_args()

    print("="*60)
    print("HDRezka Network Traffic Capture")
    print("="*60)

    capture = await capture_site_traffic(
        url=args.url,
        search_query=args.search,
        wait_time=args.wait
    )

    capture.print_summary()
    capture.save_to_file(args.output)

    print("\n[DONE] Capture complete!")


if __name__ == '__main__':
    asyncio.run(main())
