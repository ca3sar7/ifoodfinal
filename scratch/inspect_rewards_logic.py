import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Search for initSuccess or reward selection handling
pos = js.find('initSuccess')
if pos != -1:
    print("--- initSuccess ---")
    print(js[pos:pos+2000])

# Search for resolveRewardById or REWARDS object definition
pos2 = js.find('resolveRewardById')
if pos2 != -1:
    print("\n--- resolveRewardById ---")
    print(js[pos2:pos2+1500])

