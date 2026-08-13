import os
import re

target_dir = 'c:/xampp/htdocs/ifood'

matches = []

for root, dirs, files in os.walk(target_dir):
    if 'scratch' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith(('.js', '.html', '.css')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                found = re.findall(r'[\'"](/api/[^\'"]+)[\'"]', content)
                if found:
                    matches.append((os.path.relpath(fp, target_dir), found))

print("Remaining hardcoded /api/ matches count:", len(matches))
for path, urls in matches:
    print(f"  [{path}]: {urls}")

