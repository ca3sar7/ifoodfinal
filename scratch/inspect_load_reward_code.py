import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('function loadRewardSelection')
if pos != -1:
    print("--- loadRewardSelection ---")
    print(js[pos:pos+1000])

pos2 = js.find('function saveRewardSelection')
if pos2 != -1:
    print("\n--- saveRewardSelection ---")
    print(js[pos2:pos2+1000])

