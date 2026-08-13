import os
import re

target_dir = 'c:/xampp/htdocs/ifood'

matches = []

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(('.js', '.html', '.css')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                found = re.findall(r'[\'"](/api/[^\'"]+)[\'"]', content)
                if found:
                    matches.append((os.path.relpath(fp, target_dir), found))

print("Found API fetches in files:")
for path, urls in matches:
    print(f"\n{path}:")
    for u in set(urls):
        print("  -", u)

