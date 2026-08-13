import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find fetch calls, endpoints, or API URLs
fetch_matches = re.findall(r'fetch\([^\)]+\)', js)
print("--- FETCH CALLS FOUND ---")
for fm in fetch_matches:
    print(" -", fm[:200])

# Find all URLs matching http(s):// or endpoints in script.js
urls = re.findall(r'https?://[^\s\'"\)]+', js)
print("\n--- ALL HTTP URLS IN SCRIPT.JS ---")
for u in set(urls):
    print(" -", u)

# Check CEP lookup logic specifically
cep_block = re.search(r'function initCep.*?\n\}', js, re.DOTALL)
if cep_block:
    print("\n--- INIT CEP FUNCTION ---")
    print(cep_block.group(0)[:1500])

