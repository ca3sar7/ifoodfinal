import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Look for /api/ endpoints in script.js
api_endpoints = re.findall(r'[\'"](/api/[^\'"]+)[\'"]', js)
print("API Endpoints referenced in script.js:")
for ep in set(api_endpoints):
    print(" -", ep)

# Search for postPixCreateWithSessionRetry definition
pix_retry = re.search(r'async function postPixCreateWithSessionRetry.*?\n\}', js, re.DOTALL)
if pix_retry:
    print("\n--- postPixCreateWithSessionRetry ---")
    print(pix_retry.group(0)[:1500])

