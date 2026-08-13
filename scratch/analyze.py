import os
import re
import urllib.request

base_url = 'https://bagfood.vercel.app/'

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

with open('scratch/downloaded_site/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

with open('scratch/downloaded_site/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

all_text = js_content + '\n' + css_content + '\n' + html_content

# Find image/video assets
asset_pattern = r'assets/[a-zA-Z0-9_\-\./\?]+\.(?:webp|png|jpg|jpeg|gif|mp4|webm|mp3|wav|svg)'
found_assets = list(set(re.findall(asset_pattern, all_text, re.IGNORECASE)))
print('Found assets:', found_assets)

# Also find any mp4, webm, jpg, webp, png anywhere in text
all_media = list(set(re.findall(r'[\'"]([^\'"]+\.(?:mp4|webm|webp|png|jpg|jpeg|gif|svg))[\'"]', all_text, re.IGNORECASE)))
print('All media found:', all_media)

os.makedirs('scratch/downloaded_site/assets', exist_ok=True)
for a in found_assets + [m for m in all_media if m.startswith('assets/')]:
    url = base_url + a.lstrip('/')
    dest = os.path.join('scratch/downloaded_site', a)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest):
        print(f'Downloading {url} to {dest}')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
                out.write(resp.read())
            print(f'Successfully saved {dest}, size: {os.path.getsize(dest)}')
        except Exception as e:
            print(f'Error downloading {url}: {e}')

