import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

pos = bg.find('var resolveEarlyBackTarget')
if pos != -1:
    print("--- backguard.js execution ---")
    print(bg[pos+1000:pos+3000])

