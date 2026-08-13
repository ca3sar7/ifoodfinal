import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

print("--- backguard.js ---")
print(bg[:3000])

