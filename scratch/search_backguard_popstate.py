import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos = bg.find('popstate')
if pos != -1:
    print(bg[pos-100:pos+1500])

