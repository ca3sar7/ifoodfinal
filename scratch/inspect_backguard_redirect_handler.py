import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos = bg.find('resolveEarlyBackTarget')
if pos != -1:
    print(bg[pos+500:pos+3500])

