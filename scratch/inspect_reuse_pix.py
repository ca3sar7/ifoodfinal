import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('canReuseRecentPixCharge')
if pos != -1:
    print("--- canReuseRecentPixCharge ---")
    print(js[pos:pos+1500])

