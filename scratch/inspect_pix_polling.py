import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('/api/pix/status')
if pos != -1:
    print("Found /api/pix/status at char", pos)
    print(js[max(0, pos-200):min(len(js), pos+1500)])

