import os
import re
import urllib.parse
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_url = 'https://bagfood.vercel.app/'
dir_path = 'scratch/downloaded_site'

media_set = set()

for root, dirs, files in os.walk(dir_path):
    for f in files:
        if f.endswith(('.html', '.css', '.js')):
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                
                # find src= or href= or url() or quotes with assets or extensions
                matches = re.findall(r'(?:src|href|url)\s*=\s*[\'"]([^\'"]+)[\'"]', content, re.IGNORECASE)
                matches += re.findall(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', content, re.IGNORECASE)
                matches += re.findall(r'[\'"]([^\'"]+\.(?:webp|png|jpg|jpeg|gif|svg|mp4|webm|m3u8|mp3|wav|ogg|ttf|woff|woff2))[\'"]', content, re.IGNORECASE)
                
                for m in matches:
                    m = m.strip()
                    if not m.startswith('http') and not m.startswith('//') and not m.startswith('data:'):
                        media_set.add(m)
                    elif m.startswith('https://bagfood.vercel.app/'):
                        media_set.add(m.replace('https://bagfood.vercel.app/', ''))

print(f"Total media items found: {len(media_set)}")

os.makedirs('scratch/downloaded_site/assets', exist_ok=True)

for item in sorted(media_set):
    # clean query string if any for local path, but keep for url if needed
    clean_item = item.split('?')[0].lstrip('/')
    if not clean_item or clean_item.endswith(('.html', '.js', '.css', '.com', '.br')):
        continue
    
    url = urllib.parse.urljoin(base_url, item)
    dest = os.path.join(dir_path, clean_item)
    
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    print(f"Downloading {url} -> {dest}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
            out.write(resp.read())
        print(f"  OK: {os.path.getsize(dest)} bytes")
    except Exception as e:
        print(f"  FAIL: {e}")

