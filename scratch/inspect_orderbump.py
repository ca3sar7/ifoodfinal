import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/orderbump.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("--- orderbump.html ---")
print(html)

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('initOrderBump')
if pos != -1:
    print("\n--- initOrderBump function ---")
    print(js[pos:pos+1500])

