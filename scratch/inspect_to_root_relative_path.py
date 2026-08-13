import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('function toRootRelativePath')
if pos != -1:
    print("--- script.js toRootRelativePath ---")
    print(js[pos:pos+800])

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos2 = bg.find('toRootRelativePath')
if pos2 != -1:
    print("--- backguard.js toRootRelativePath ---")
    print(bg[pos2:pos2+800])

