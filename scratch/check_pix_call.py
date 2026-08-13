import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('c:/xampp/htdocs/ifood/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Let's check how postPixCreateWithSessionRetry is called in createPixCharge
match = re.search(r'const \{ response, body \} = await postPixCreateWithSessionRetry\(payload\);', js)
if match:
    print("Found postPixCreateWithSessionRetry call!")

