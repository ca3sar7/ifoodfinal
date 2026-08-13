import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find toRootRelativePath and redirect definition
pos = js.find('function toRootRelativePath')
if pos != -1:
    print("--- toRootRelativePath ---")
    print(js[pos:pos+1500])

pos2 = js.find('function redirect')
if pos2 != -1:
    print("\n--- redirect ---")
    print(js[pos2:pos2+1500])

