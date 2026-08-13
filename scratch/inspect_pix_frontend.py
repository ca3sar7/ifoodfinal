import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Search for /api/pix/status calls or status checking logic
status_calls = re.findall(r'.{0,100}/api/pix/status.{0,200}', js, re.DOTALL)
print("--- STAGE & STATUS LOGIC IN SCRIPT.JS ---")
for sc in status_calls:
    print("MATCH:", sc)
    print("-" * 50)

