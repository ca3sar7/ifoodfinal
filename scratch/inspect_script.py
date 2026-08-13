import sys
import re
import urllib.parse
import urllib.request
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

print("First 2000 chars of script.js:")
print(js[:2000])

print("\nLast 2000 chars of script.js:")
print(js[-2000:])

# Search for any video URLs (mp4, m3u8, webm, etc.) or video tags or vsl links
videos = re.findall(r'https?://[^\s\'"]+\.(?:mp4|webm|m3u8|mov)', js, re.IGNORECASE)
print("\nVideo URLs found:", set(videos))

# Search for iframe, vimeo, youtube, panda, vturb, etc.
vsl_matches = re.findall(r'(https?://[^\s\'"]*(?:vturb|panda|youtube|vimeo|wistia|cloudfront|cdn)[^\s\'"]*)', js, re.IGNORECASE)
print("\nVSL/Video embeds found:", set(vsl_matches))

# Search for all strings matching URLs or assets
all_urls = re.findall(r'(https?://[^\s\'"]+|assets/[^\s\'"]+)', js)
print("\nUnique URLs/Assets in script.js:")
for url in sorted(set(all_urls)):
    if any(ext in url.lower() for ext in ['.png', '.webp', '.jpg', '.jpeg', '.mp4', '.svg', '.gif', '.mp3', '.webm']):
        print("  -", url)

