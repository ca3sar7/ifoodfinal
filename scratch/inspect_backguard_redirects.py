import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos = bg.find('resolvePaidPixTarget')
if pos != -1:
    print("--- backguard.js redirects ---")
    print(bg[pos:pos+3000])

