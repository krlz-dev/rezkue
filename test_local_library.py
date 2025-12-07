#!/usr/bin/env python3
"""
Test script to verify local HdRezkaApi library works correctly
"""
import sys
import os

# Add local lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from HdRezkaApi import HdRezkaApi

def test_import():
    """Test that the library imports correctly"""
    print("✓ HdRezkaApi imported successfully")
    print(f"  Version: {HdRezkaApi.__version__}")

def test_basic_page_load():
    """Test basic page loading"""
    test_url = "https://rezka.ag/series/horror/79810-ono-dobro-pozhalovat-v-derri-2025-latest.html"

    print(f"\nTesting with URL: {test_url}")

    try:
        rezka = HdRezkaApi(test_url)
        print(f"✓ Initialized HdRezkaApi")
        print(f"  ID: {rezka.id}")
        print(f"  Name: {rezka.name}")
        print(f"  Type: {rezka.type}")
        print(f"  Translators: {list(rezka.translators.keys())[:3]}...")  # First 3

        if rezka.type == 'tv_series':
            print(f"  Series Info: {len(rezka.seriesInfo)} translators")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stream_fetch():
    """Test stream fetching (this will likely fail on datacenter IPs)"""
    test_url = "https://rezka.ag/series/horror/79810-ono-dobro-pozhalovat-v-derri-2025-latest.html"

    print(f"\n\nTesting stream fetch...")
    print("Note: This will fail on datacenter IPs (Render, AWS, etc.)")

    try:
        rezka = HdRezkaApi(test_url)

        if rezka.type == 'tv_series':
            # Get first translator
            first_translator = list(rezka.translators.values())[0]
            print(f"  Using translator: {first_translator}")

            # Try to get stream for S01E01
            stream = rezka.getStream(season="1", episode="1", translation=first_translator)

            print(f"✓ Stream fetched successfully!")
            print(f"  Available qualities: {list(stream.videos.keys())}")
            return True
    except ValueError as e:
        if "blocking" in str(e).lower() or "IP address" in str(e):
            print(f"✗ IP BLOCKING DETECTED: {e}")
            print("  This is expected on datacenter/cloud hosting IPs")
            print("  See IP_BLOCKING_ISSUE.md for solutions")
            return None  # None = expected failure
        else:
            print(f"✗ Error: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("HdRezkaApi Local Library Test")
    print("="*60)

    test_import()

    page_ok = test_basic_page_load()
    stream_result = test_stream_fetch()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Library import: ✓")
    print(f"Page loading: {'✓' if page_ok else '✗'}")

    if stream_result is True:
        print(f"Stream fetching: ✓ (residential IP)")
    elif stream_result is None:
        print(f"Stream fetching: ✗ (datacenter IP blocked - EXPECTED)")
    else:
        print(f"Stream fetching: ✗ (unexpected error)")

    print("\nSee IP_BLOCKING_ISSUE.md for details on the blocking issue.")
