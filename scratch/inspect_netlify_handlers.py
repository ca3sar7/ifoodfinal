import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Inspect postPixCreateWithSessionRetry
pos = js.find('postPixCreateWithSessionRetry')
if pos != -1:
    print("--- postPixCreateWithSessionRetry ---")
    print(js[pos:pos+1200])

# Inspect isOrderBumpEnabled
pos2 = js.find('isOrderBumpEnabled')
if pos2 != -1:
    print("\n--- isOrderBumpEnabled ---")
    print(js[pos2:pos2+800])

