#!/usr/bin/env python3
"""
Manual Navigation Capture Tool for HDRezka
Opens browser and captures network traffic while you manually navigate
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import argparse

class ManualCaptureSession:
    def __init__(self, output_file='manual_capture.json'):
        self.output_file = output_file
        self.requests = []

    async def should_block_request(self, route, request):
        """Block unwanted requests like ads, tracking, overlays"""
        url = request.url

        block_patterns = [
            'ovpaid.php',
            '/ads/',
            'doubleclick.net',
            'googletagmanager',
            'google-analytics',
            'yandex-metrica',
            '/banner',
            '/counter',
            '.gif?',
        ]

        for pattern in block_patterns:
            if pattern in url.lower():
                print(f"[BLOCKED] {url}")
                await route.abort()
                return

        await route.continue_()

    async def on_request(self, request):
        """Capture outgoing request"""
        req_data = {
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'timestamp': datetime.now().isoformat()
        }

        # Capture POST data
        if request.method == 'POST':
            try:
                req_data['postData'] = request.post_data
                print(f"[POST] {request.url}")
                if request.post_data:
                    print(f"  Data: {request.post_data[:200]}")
            except:
                pass

        # Store for later response matching
        req_data['request_id'] = id(request)
        self.requests.append(req_data)

    async def on_response(self, response):
        """Capture response data"""
        url = response.url

        # Find the matching request
        request_id = id(response.request)
        matching_req = None
        for req in self.requests:
            if req.get('request_id') == request_id:
                matching_req = req
                break

        if not matching_req:
            return

        # Add response info
        matching_req['status'] = response.status
        matching_req['statusText'] = response.status_text
        matching_req['response_headers'] = dict(response.headers)

        # Capture response body for important endpoints
        important_patterns = [
            'ajax/get_cdn_series',
            'ajax/get_cdn_movies',
            '/ajax/',
            '.m3u8',
            '/search/',
        ]

        should_capture_body = any(pattern in url for pattern in important_patterns)

        if should_capture_body:
            try:
                body = await response.body()
                body_text = body.decode('utf-8', errors='ignore')
                matching_req['response_body'] = body_text

                # Print summary for AJAX calls
                if 'ajax' in url.lower():
                    print(f"[AJAX RESPONSE] {url}")
                    print(f"  Status: {response.status}")
                    print(f"  Body preview: {body_text[:150]}")
                    print()

            except Exception as e:
                matching_req['response_error'] = str(e)

    async def run(self, start_url='https://rezka.ag/', wait_time=300):
        """
        Run the manual capture session

        Args:
            start_url: URL to start from
            wait_time: How long to keep browser open (seconds)
        """
        print("=" * 70)
        print("MANUAL CAPTURE SESSION")
        print("=" * 70)
        print(f"Starting URL: {start_url}")
        print(f"Will capture for: {wait_time} seconds")
        print()
        print("INSTRUCTIONS:")
        print("1. The browser will open automatically")
        print("2. Navigate manually to any content you want")
        print("3. Search for series/movies")
        print("4. Select translations, seasons, episodes")
        print("5. Click play button")
        print("6. All network traffic will be captured")
        print()
        print("When done, close the browser or wait for timeout.")
        print("=" * 70)
        print()

        async with async_playwright() as p:
            # Launch browser with visible UI
            browser = await p.firefox.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create context with proper headers
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                }
            )

            page = await context.new_page()

            # Set up request/response interception
            await page.route('**/*', self.should_block_request)
            page.on('request', self.on_request)
            page.on('response', self.on_response)

            print(f"[NAVIGATE] Opening {start_url}")
            await page.goto(start_url, wait_until='domcontentloaded', timeout=30000)

            print()
            print("✅ Browser is ready! Navigate manually now...")
            print(f"   Capturing network traffic for {wait_time} seconds...")
            print()

            try:
                # Wait for specified time or until browser is closed
                await page.wait_for_timeout(wait_time * 1000)
            except Exception as e:
                print(f"\n[INFO] Browser closed or session ended: {e}")

            print("\n[SAVING] Captured data...")
            await browser.close()

        # Save captured data
        self.save_capture()

    def save_capture(self):
        """Save captured requests to JSON file"""
        output = {
            'capture_time': datetime.now().isoformat(),
            'total_requests': len(self.requests),
            'requests': []
        }

        # Clean up request data (remove internal IDs)
        for req in self.requests:
            clean_req = {k: v for k, v in req.items() if k != 'request_id'}
            output['requests'].append(clean_req)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Capture saved to: {self.output_file}")
        print(f"   Total requests captured: {len(self.requests)}")

        # Print summary of important captures
        ajax_calls = [r for r in self.requests if 'ajax' in r['url'].lower()]
        post_calls = [r for r in self.requests if r['method'] == 'POST']
        m3u8_calls = [r for r in self.requests if '.m3u8' in r['url']]

        print(f"\n📊 Summary:")
        print(f"   AJAX calls: {len(ajax_calls)}")
        print(f"   POST requests: {len(post_calls)}")
        print(f"   HLS manifests: {len(m3u8_calls)}")

        if post_calls:
            print(f"\n📤 POST Requests Captured:")
            for post in post_calls[:10]:  # Show first 10
                print(f"   - {post['url']}")
                if post.get('postData'):
                    print(f"     Data: {post['postData'][:100]}")


async def main():
    parser = argparse.ArgumentParser(description='Manual capture session for HDRezka')
    parser.add_argument('--url', default='https://rezka.ag/', help='Starting URL')
    parser.add_argument('--wait', type=int, default=300, help='Wait time in seconds (default: 300 = 5 min)')
    parser.add_argument('--output', default='manual_capture.json', help='Output JSON file')

    args = parser.parse_args()

    session = ManualCaptureSession(output_file=args.output)
    await session.run(start_url=args.url, wait_time=args.wait)


if __name__ == '__main__':
    asyncio.run(main())
