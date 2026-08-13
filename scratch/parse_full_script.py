import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/downloaded_site/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('scratch/downloaded_site/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('scratch/downloaded_site/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

with open('scratch/downloaded_site/backguard.js', 'r', encoding='utf-8') as f:
    bg = f.read()

print("HTML Length:", len(html))
print("CSS Length:", len(css))
print("JS Length:", len(js))
print("Backguard JS Length:", len(bg))

# Let's save a pretty print of JS or print out all functions/structures
with open('scratch/script_dump.txt', 'w', encoding='utf-8') as f:
    f.write(js)

print("Saved script_dump.txt")
