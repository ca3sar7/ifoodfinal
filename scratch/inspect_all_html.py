import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

pages = [
    'index.html',
    'quiz.html',
    'dados.html',
    'endereco.html',
    'processando.html',
    'checkout.html',
    'pix-loading.html',
    'pix.html',
    'orderbump.html',
    'upsell.html',
    'upsell-correios.html',
    'upsell-iof.html',
    'sucesso.html'
]

for p in pages:
    file_path = os.path.join('scratch/downloaded_site', p)
    print(f"\n==================== {p} ====================")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("FILE NOT FOUND")

