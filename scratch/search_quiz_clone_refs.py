import os
import re

target_dir = 'c:/xampp/htdocs/ifood'

matches = []

for root, dirs, files in os.walk(target_dir):
    if 'scratch' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith(('.js', '.html', '.css', '.php', '.htaccess', '.json')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'quiz-clone' in content:
                    matches.append((os.path.relpath(fp, target_dir), re.findall(r'.{0,50}quiz-clone.{0,50}', content)))

print("Found references to 'quiz-clone':")
for path, refs in matches:
    print(f"\n[{path}]:")
    for r in set(refs):
        print("  -", r.strip())

