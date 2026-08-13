import urllib.request
import urllib.parse
import os

base_url = 'https://bagfood.vercel.app/'
items = [
    'assets/__task____fix_ifood_logo_on_jacket_,_202603260102 (1).webp',
    'assets/__task____isolate_ifood_delivery_box_white_background_,_202603260112 (1).webp'
]

for item in items:
    encoded_item = urllib.parse.quote(item)
    url = base_url + encoded_item
    dest = os.path.join('scratch/downloaded_site', item)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"Downloading {url} -> {dest}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
            out.write(resp.read())
        print(f"  OK: {os.path.getsize(dest)} bytes")
    except Exception as e:
        print(f"  FAIL: {e}")

