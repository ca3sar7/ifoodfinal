import urllib.request
import os

base_url = 'https://bagfood.vercel.app/'

pages = [
    'index.html',
    'quiz.html',
    'processando.html',
    'dados.html',
    'endereco.html',
    'checkout.html',
    'pix-loading.html',
    'pix.html',
    'orderbump.html',
    'upsell.html',
    'upsell-correios.html',
    'upsell-iof.html',
    'sucesso.html'
]

os.makedirs('scratch/downloaded_site', exist_ok=True)

for page in pages:
    url = base_url + page
    dest = os.path.join('scratch/downloaded_site', page)
    print(f"Downloading {url} to {dest}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
            out.write(resp.read())
        print(f"Success {page}: {os.path.getsize(dest)} bytes")
    except Exception as e:
        print(f"Error {page}: {e}")

