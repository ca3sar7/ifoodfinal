import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Inspect createPixCharge
pix_create = re.search(r'async function createPixCharge.*?\n\}', js, re.DOTALL)
if pix_create:
    print("--- createPixCharge ---")
    print(pix_create.group(0)[:2000])

# Inspect initPix
init_pix = re.search(r'function initPix\(\).*?\n\}', js, re.DOTALL)
if init_pix:
    print("\n--- initPix ---")
    print(init_pix.group(0)[:2000])

