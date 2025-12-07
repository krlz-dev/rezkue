#!/usr/bin/env python3
"""
Analyze captured network data to extract video sources and API patterns
"""

import json
import sys
from urllib.parse import urlparse, parse_qs
from collections import defaultdict


def analyze_capture(filename):
    """Analyze the captured network data"""

    with open(filename, 'r') as f:
        data = json.load(f)

    print("="*60)
    print(f"ANALYSIS OF: {filename}")
    print("="*60)
    print(f"\nCapture Time: {data['capture_time']}")
    print(f"Total Requests: {data['summary']['total_requests']}")
    print(f"Video Sources: {data['summary']['video_sources']}")
    print(f"API Calls: {data['summary']['api_calls']}")

    # Extract unique video domains
    video_domains = set()
    video_patterns = defaultdict(list)

    for video in data['video_sources']:
        url = video['url']
        parsed = urlparse(url)
        video_domains.add(parsed.netloc)

        # Categorize by type
        if 'manifest.m3u8' in url:
            video_patterns['HLS Manifests'].append(url)
        elif '.ts' in url:
            video_patterns['HLS Segments'].append(url)
        elif '.mp4' in url:
            video_patterns['MP4 Files'].append(url)

    print("\n" + "="*60)
    print("VIDEO CDN DOMAINS")
    print("="*60)
    for domain in sorted(video_domains):
        print(f"  - {domain}")

    print("\n" + "="*60)
    print("VIDEO SOURCE BREAKDOWN")
    print("="*60)
    for pattern_type, urls in video_patterns.items():
        print(f"\n{pattern_type}: {len(urls)}")
        # Show first 3 unique URLs of each type
        unique_urls = list(set(urls))[:3]
        for url in unique_urls:
            print(f"  - {url}")

    # Find important API calls
    print("\n" + "="*60)
    print("KEY API ENDPOINTS")
    print("="*60)

    important_apis = []
    for api in data['api_calls']:
        url = api['url']
        method = api['method']

        # Filter for video-related APIs
        if any(keyword in url.lower() for keyword in ['cdn', 'video', 'stream', 'player', 'ajax']):
            important_apis.append(f"{method} {url}")

    # Remove duplicates and show unique ones
    for api in sorted(set(important_apis)):
        print(f"  - {api}")

    # Try to find API responses with video data
    print("\n" + "="*60)
    print("API RESPONSES WITH POTENTIAL VIDEO DATA")
    print("="*60)

    responses_with_body = []
    for response in data['all_responses']:
        if 'body' in response and response['body']:
            url = response['url']
            if any(keyword in url.lower() for keyword in ['cdn', 'ajax', 'get_cdn']):
                responses_with_body.append({
                    'url': url,
                    'body': response['body'][:500]  # First 500 chars
                })

    for resp in responses_with_body[:3]:  # Show first 3
        print(f"\nURL: {resp['url']}")
        print(f"Body preview: {resp['body'][:200]}...")

    # Extract search URL pattern
    print("\n" + "="*60)
    print("URL PATTERNS DISCOVERED")
    print("="*60)

    all_urls = [req['url'] for req in data['all_requests']]

    # Find search URLs
    search_urls = [url for url in all_urls if 'search' in url.lower()]
    if search_urls:
        print(f"\nSearch URL pattern:")
        print(f"  {search_urls[0]}")

    # Find video page URLs
    video_page_urls = [url for url in all_urls if '/films/' in url or '/series/' in url]
    if video_page_urls:
        print(f"\nVideo page URLs found: {len(set(video_page_urls))}")
        for url in list(set(video_page_urls))[:2]:
            print(f"  - {url}")

    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)
    print("""
To build a simple video player client:

1. Search for videos:
   GET https://rezka.ag/search/?do=search&subaction=search&q=QUERY

2. Get video page:
   Navigate to the video URL from search results
   (e.g., /films/ACTION/12345-movie-name.html)

3. Get video sources:
   POST https://rezka.ag/ajax/get_cdn_series/
   (Check the network capture for required parameters)

4. Play video:
   Use the returned HLS manifest URL (.m3u8)
   Stream from CDN: apollo.stream.voidboost.cc

5. Block ads/overlays:
   Block: code.21wiz.com/ovpaid.php
    """)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'network_capture.json'

    analyze_capture(filename)
