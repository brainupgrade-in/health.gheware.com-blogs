#!/usr/bin/env python3
"""Submit URLs to IndexNow (Bing, Yandex, Naver, Seznam)."""
import json
import sys
import urllib.request

INDEXNOW_KEY = "f970ec769364492583a631e0f3c25f55"
HOST = "health.gheware.com"
KEY_LOCATION = f"https://{HOST}/blog/{INDEXNOW_KEY}.txt"

ENGINES = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]

def submit_urls(urls: list[str]):
    """Submit a list of URLs to all IndexNow engines."""
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode()

    results = {}
    for engine in ENGINES:
        try:
            req = urllib.request.Request(
                engine,
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=15)
            results[engine] = f"OK ({resp.status})"
        except urllib.error.HTTPError as e:
            results[engine] = f"HTTP {e.code}"
        except Exception as e:
            results[engine] = f"Error: {e}"

    return results

def get_all_blog_urls():
    """Get all URLs from the sitemap."""
    import xml.etree.ElementTree as ET
    sitemap_url = f"https://{HOST}/blog/sitemap.xml"
    req = urllib.request.Request(sitemap_url)
    resp = urllib.request.urlopen(req, timeout=15)
    tree = ET.parse(resp)
    root = tree.getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in root.findall(".//s:loc", ns)]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("Fetching all URLs from sitemap...")
        urls = get_all_blog_urls()

    print(f"Submitting {len(urls)} URLs to IndexNow engines...")
    results = submit_urls(urls)
    for engine, status in results.items():
        print(f"  {engine}: {status}")
