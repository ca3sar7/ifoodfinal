import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

match = re.search(r'function toRootRelativePath.*?\n\}', js, re.DOTALL)
if match:
    print("toRootRelativePath function:")
    print(match.group(0))
else:
    print("Function not found, searching for string 'toRootRelativePath':")
    matches = re.findall(r'.{0,100}toRootRelativePath.{0,100}', js)
    for m in matches:
        print(" -", m)

